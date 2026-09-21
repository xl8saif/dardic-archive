"""Language detection, direction and slug utilities for the sync pipeline."""
from __future__ import annotations

import re
import unicodedata

# Codes that render right-to-left on the site.
RTL_CODES = {"ur", "ar", "mvb", "scl", "fa", "ps", "sd", "ks"}

# Codes rendered in Nastaliq (others in Amiri if Arabic-script).
NASTALIQ_CODES = {"ur"}

# Latin transliteration map for Urdu/Arabic script chars used in slugs.
_TRANSLIT = {
    "ا": "a", "آ": "aa", "ب": "b", "پ": "p", "ت": "t", "ٹ": "t", "ث": "s",
    "ج": "j", "چ": "ch", "ح": "h", "خ": "kh", "د": "d", "ڈ": "d", "ذ": "z",
    "ر": "r", "ڑ": "r", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "ص": "s",
    "ض": "z", "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
    "ک": "k", "گ": "g", "ل": "l", "م": "m", "ن": "n", "ں": "n", "و": "o",
    "ہ": "h", "ھ": "h", "ء": "", "ی": "i", "ے": "e", "ي": "y", "ك": "k",
    "ة": "h", "أ": "a", "إ": "i", "ؤ": "o", "ئ": "e", "ى": "a",
}

_ARABIC_RE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
_LATIN_RE = re.compile(r"[A-Za-z]")


def detect_script(text: str) -> str:
    """Rough script detection from character counts."""
    if not text:
        return "latin"
    arabic = len(_ARABIC_RE.findall(text))
    latin = len(_LATIN_RE.findall(text))
    if arabic == 0 and latin == 0:
        return "latin"
    return "arabic" if arabic >= latin else "latin"


def detect_lang(text: str, folder_hint: str | None = None,
                filename_tag: str | None = None) -> str:
    """Resolve the language: filename tag > text detection > folder hint > en."""
    if filename_tag:
        return filename_tag.lower()
    script = detect_script(text[:4000])
    if script == "arabic":
        # Urdu dominates this corpus; folder hints can refine to ar/mvb/scl.
        return folder_hint or "ur"
    return folder_hint or "en"


def dir_for(lang: str) -> str:
    return "rtl" if lang in RTL_CODES else "ltr"


def slugify(text: str, fallback: str = "untitled") -> str:
    """ASCII slug; Arabic-script titles are transliterated, not dropped."""
    text = unicodedata.normalize("NFKC", text).strip()
    out: list[str] = []
    for ch in text:
        if ch in _TRANSLIT:
            out.append(_TRANSLIT[ch])
        elif ch.isascii() and ch.isalnum():
            out.append(ch)
        elif ch.isspace() or ch in "-_":
            out.append("-")
    slug = re.sub(r"[\s_-]{2,}", "-", "".join(out)).strip("- ").lower()
    return slug[:80].strip("-") or fallback


def filename_tag(name: str, allowed: list[str]) -> str | None:
    """Extract a [xx] language tag from a filename, e.g. 'Indus [scl].docx'."""
    m = re.search(r"\[([a-z]{2,3})\]", name, re.IGNORECASE)
    if m and m.group(1).lower() in allowed:
        return m.group(1).lower()
    return None
