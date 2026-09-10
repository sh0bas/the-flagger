---
name: testing-conventions
description: How Flagger's test suite is structured and run (pytest, backend-only, no DB or fixtures), and what a new test must cover for an endpoint, a scoring/anti-cheat change, or a normalization change. Use when writing or modifying tests, when asked whether a change needs test coverage, or before claiming a backend change is verified.
---

# Flagger testing conventions

## Running the suite

```bash
cd backend && .venv/bin/python -m pytest tests/ -q
```

Or in the container: `docker-compose exec backend pytest tests/` — note this runs the pinned `pytest==7.4.3` from `requirements.txt`, while the venv above has drifted to 9.x. Same tests, different runner.

The suite is fast (well under a second) because it touches no database. There is no `pytest.ini`/`pyproject.toml` — pytest runs on defaults, and `tests/conftest.py` does the one piece of setup that matters:

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

That's the *only* thing conftest does. Put the path shim nowhere else; individual test files must not repeat it.

One `PydanticDeprecatedSince20` warning is expected (the `class Config` style in response schemas). It is not a failure.

## What exists

| File | Covers |
|---|---|
| `tests/test_scoring.py` | `_points`, `grade`, `normalize_str`, `FlagQuizResult` validation |
| `tests/test_auth_schemas.py` | `RegisterRequest` password byte-length rule |
| `tests/test_rate_limit.py` | `deps.rate_limit` limiting + dict eviction |

**There is no frontend test suite** — `frontend/package.json` has no `test` script, no vitest, no jest. Frontend changes are verified with `npx tsc --noEmit`, `npm run lint`, and running the app.

## The rule this suite follows

Tests cover **logic where a silent regression costs users their scores or their account security** — not endpoints, not wiring, not CRUD.

Consequences, all deliberate:
- **No database.** No async tests, no `httpx.AsyncClient`, no TestClient, no session fixtures, no `pytest-asyncio` (it isn't even installed). Everything under test is a pure function or a plain Pydantic model.
- **No mocking library.** The two things that need substitution are done by hand:
  - a `SimpleNamespace` stand-in (`FakeRequest` in `test_rate_limit.py`) for the one attribute the code reads,
  - `monkeypatch.setattr(time, "monotonic", lambda: t[0])` to drive the clock deterministically.
- **Module-level state gets an autouse fixture to reset it**, e.g. `clean_hits` clearing `deps._hits` before and after each test.

Don't add a DB-backed integration layer for a routine change. If a change genuinely can't be tested without one, say so rather than quietly skipping coverage.

## Style

- Grouped in plain `class TestXxx:` containers with no base class — `TestPoints`, `TestNormalize`, `TestGrade`.
- Test names state the rule, not the mechanics: `test_streak_bonus_is_capped`, `test_unknown_country_id_is_never_correct`, `test_expired_clients_are_evicted_not_kept_forever`.
- Bare `assert`. Rejection paths use `with pytest.raises(ValidationError):` / `pytest.raises(HTTPException)`, asserting `exc.value.status_code` where the code matters.
- Docstrings explain *why the case matters*, usually naming the real-world failure — e.g. "iOS substitutes the curly form as you type, so a mismatch here marks correct answers wrong for every phone user." Keep that habit; it's what makes these tests survivable.
- Local helpers over fixtures for building inputs (`_answers(*pairs)`, `_result(*country_ids)`, `_register(password)`).

## What a new test must cover

**Changing `_points` or `grade` (`app/api/routes/games.py`):**
- each bonus tier at its exact boundary (`4_999` vs `5_000` vs `9_999` vs `10_000`)
- the streak threshold at 2/3, and the `MAX_STREAK_BONUS` cap holding at 20, 21, and an absurd value
- streak resets to zero on a wrong answer
- an empty answer list
- **the anti-cheat cases**: a wrong answer scores nothing, and an unknown `country_id` is never correct
- if you touched the formula, update `calcScore()` in `frontend/src/hooks/useQuizReducer.ts` in the same change — it's a hand-synced display-only mirror, and drift is the actual risk being guarded against here

**Changing `normalize_str` (`app/services/country_service.py`):**
- diacritics stripped, curly apostrophes (U+2018/U+2019) folded to `'`, case and surrounding whitespace normalized
- **non-Latin scripts survive**: assert Cyrillic/Greek input is non-empty *and* that two different non-Latin names don't normalize equal. A prior `.encode("ascii", "ignore")` collapsed both to `""`, making distinct answers compare equal — a false *positive*, not just a missed match.
- characters NFD doesn't decompose (`ß`, `ø`) are preserved — note `.lower()` does **not** fold `ß` to `ss`; assert the actual output
- it must stay equivalent to `normalizeForComparison()` in `frontend/src/hooks/useQuizReducer.ts`

**Changing `FlagQuizResult` / `FlagQuizAnswer` (`app/schemas/game.py`):**
- both the accepted and the rejected shape
- **omitted vs. empty** are separate tests — Pydantic doesn't validate defaults, so `min_length=1` on a field with a default silently passes when the field is absent
- duplicate `country_id`s rejected (the farm-one-easy-flag exploit)

**Changing `deps.rate_limit`:**
- allows exactly up to `_RATE_LIMIT`, rejects the next with 429
- separate client IPs get separate budgets
- entries for fully-expired windows are evicted, so `_hits` stays bounded — drive this with a monkeypatched `time.monotonic`, never a real `sleep`
