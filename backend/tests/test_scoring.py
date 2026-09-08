"""Checks on the two pieces of logic where a silent regression costs players scores.

Both have a hand-synced counterpart in the frontend, so drift is the risk being
guarded against here, not obvious breakage.
"""
import pytest
from pydantic import ValidationError

from app.api.routes.games import _points, grade
from app.schemas.game import FlagQuizAnswer, FlagQuizResult
from app.services.country_service import normalize_str


class TestPoints:
    def test_base_only_when_slow(self):
        assert _points(11_000, 1) == 100

    def test_speed_bonuses(self):
        assert _points(4_999, 1) == 150   # < 5s
        assert _points(5_000, 1) == 125   # < 10s
        assert _points(9_999, 1) == 125
        assert _points(10_000, 1) == 100  # no bonus

    def test_streak_bonus_starts_at_three(self):
        assert _points(11_000, 2) == 100
        assert _points(11_000, 3) == 130
        assert _points(11_000, 10) == 200

    def test_bonuses_stack(self):
        assert _points(1_000, 5) == 100 + 50 + 50

    def test_streak_bonus_is_capped(self):
        """Repeating one easy answer must not let the streak bonus grow forever."""
        assert _points(11_000, 20) == 100 + 200
        assert _points(11_000, 21) == 100 + 200
        assert _points(11_000, 1000) == 100 + 200


class TestNormalize:
    def test_strips_diacritics(self):
        assert normalize_str("Côte d'Ivoire") == "cote d'ivoire"
        assert normalize_str("São Tomé") == "sao tome"

    def test_curly_apostrophe_matches_straight(self):
        """The client folds U+2019 to "'"; a bare ascii encode would delete it.

        iOS substitutes the curly form as you type, so a mismatch here marks
        correct answers wrong for every phone user.
        """
        assert normalize_str("Cote d’Ivoire") == normalize_str("Cote d'Ivoire")
        assert normalize_str("Cote d‘Ivoire") == normalize_str("Cote d'Ivoire")

    def test_case_and_whitespace(self):
        assert normalize_str("  UNITED STATES  ") == "united states"

    def test_empty(self):
        assert normalize_str("") == ""


class TestGrade:
    """Grading is what stops a tampered payload claiming an arbitrary score."""

    NAMES = {1: ["France"], 2: ["Germany", "Deutschland"], 3: ["Côte d'Ivoire"]}

    def _answers(self, *pairs):
        from app.schemas.game import FlagQuizAnswer
        return [
            FlagQuizAnswer(country_id=cid, user_answer=ans, response_ms=ms)
            for cid, ans, ms in pairs
        ]

    def test_empty_scores_zero(self):
        assert grade([], self.NAMES) == {
            "score": 0, "correct_count": 0, "max_streak": 0,
            "questions_count": 0, "avg_response_ms": 0, "answers": [],
        }

    def test_wrong_answers_score_nothing(self):
        out = grade(self._answers((1, "Spain", 100), (2, "Italy", 100)), self.NAMES)
        assert out["score"] == 0
        assert out["correct_count"] == 0
        assert all(a["correct"] is False for a in out["answers"])

    def test_unknown_country_id_is_never_correct(self):
        """A payload referencing a country that doesn't exist can't score."""
        out = grade(self._answers((999, "France", 100)), self.NAMES)
        assert out["score"] == 0
        assert out["answers"][0]["correct"] is False

    def test_alias_accepted(self):
        out = grade(self._answers((2, "deutschland", 100)), self.NAMES)
        assert out["correct_count"] == 1

    def test_diacritics_and_curly_apostrophe_accepted(self):
        out = grade(self._answers((3, "cote d’ivoire", 100)), self.NAMES)
        assert out["correct_count"] == 1

    def test_streak_resets_on_wrong(self):
        out = grade(
            self._answers(*[(1, "France", 100)] * 3, (1, "nope", 100), (1, "France", 100)),
            self.NAMES,
        )
        assert out["correct_count"] == 4
        assert out["max_streak"] == 3

    def test_derived_stats(self):
        out = grade(self._answers((1, "France", 100), (1, "nope", 300)), self.NAMES)
        assert out["questions_count"] == 2
        assert out["avg_response_ms"] == 200
        assert out["score"] == 150  # one correct, fast


class TestFlagQuizResultRejectsRepeatedCountries:
    """The API boundary, not grade(), is what stops the farm-one-flag exploit."""

    def _result(self, *country_ids):
        return FlagQuizResult(
            game_mode="gauntlet",
            answers=[
                FlagQuizAnswer(country_id=cid, user_answer="x", response_ms=100)
                for cid in country_ids
            ],
        )

    def test_unique_country_ids_accepted(self):
        self._result(1, 2, 3)  # must not raise

    def test_empty_answers_rejected(self):
        with pytest.raises(ValidationError):
            self._result()  # no country_ids -> answers=[]

    def test_omitted_answers_rejected(self):
        with pytest.raises(ValidationError):
            FlagQuizResult(game_mode="gauntlet")

    def test_repeated_country_id_rejected(self):
        with pytest.raises(ValidationError):
            self._result(1, 1, 2)
