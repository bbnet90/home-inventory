from __future__ import annotations

import unicodedata

# SQLite's LOWER()/LIKE only fold ASCII, so Turkish names such as "İstanbul" or
# "Şemsiye" never matched a lowercase query. Fold both sides in Python instead.
# The dotted/dotless i family is collapsed to a plain "i" so that "istanbul",
# "ISTANBUL", "İstanbul" and "ıstanbul" all match each other.
_I_VARIANTS = str.maketrans({"İ": "i", "I": "i", "ı": "i"})


def fold_text(value: str | None) -> str | None:
    """Normalize text for case-insensitive, Turkish-aware comparison."""
    if value is None:
        return None
    composed = unicodedata.normalize("NFC", value)
    folded = composed.translate(_I_VARIANTS).casefold()
    return unicodedata.normalize("NFC", folded)


def escape_like(value: str, escape: str = "\\") -> str:
    """Escape LIKE wildcards so user input is matched literally."""
    return (
        value.replace(escape, escape + escape)
        .replace("%", escape + "%")
        .replace("_", escape + "_")
    )
