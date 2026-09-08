"""Country name normalization.

Must stay equivalent to normalizeForComparison() in
frontend/src/hooks/useQuizReducer.ts — the client decides what to show the
player, the server decides what to score, and a disagreement silently marks
correct answers wrong.
"""

import unicodedata

# iOS and macOS substitute a curly apostrophe as you type. Fold it to ASCII
# *before* the ascii encode below, which would otherwise drop it entirely and
# turn "Cote d'Ivoire" into "cote divoire" on the server but "cote d'ivoire"
# on the client.
_APOSTROPHES = str.maketrans({"\u2019": "'", "\u2018": "'", "`": "'"})


def normalize_str(s: str) -> str:
    """Strip diacritics, unify apostrophes, and lowercase for comparison."""
    return (
        unicodedata.normalize("NFD", s.translate(_APOSTROPHES))
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
        .strip()
    )
