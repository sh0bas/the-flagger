"""Country name normalization.

Must stay equivalent to normalizeForComparison() in
frontend/src/hooks/useQuizReducer.ts — the client decides what to show the
player, the server decides what to score, and a disagreement silently marks
correct answers wrong.
"""

import re
import unicodedata

# iOS and macOS substitute a curly apostrophe as you type. Fold it to ASCII
# before stripping combining marks below.
_APOSTROPHES = str.maketrans({"\u2019": "'", "\u2018": "'", "`": "'"})

# Same range the client strips in normalizeForComparison(). Deliberately not
# .encode("ascii", "ignore"): that also silently drops any non-ASCII
# character NFD doesn't decompose (\u00df, \u00f8, and every non-Latin-script name/
# alt_name in the catalog), which the client leaves untouched - two distinct
# native-script names then both normalized to "" and compared equal.
_COMBINING_MARKS = re.compile(r"[\u0300-\u036f]")


def normalize_str(s: str) -> str:
    """Strip diacritics, unify apostrophes, and lowercase for comparison."""
    decomposed = unicodedata.normalize("NFD", s.translate(_APOSTROPHES))
    return _COMBINING_MARKS.sub("", decomposed).lower().strip()
