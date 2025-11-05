# utils/spell.py
import os
import re
from spellchecker import SpellChecker

# Add/adjust to your domain
WHITELIST = {
    "Devant", "SN25", "SHT", "SHA", "PN", "Ben1234", "Bengali",
    "SRU", "WhatsApp", "Kiwi", "Academics", "Signin", "svg",
    "Dashboard", "Session", "Sessions", "Check", "Checkingv",
    "EN", "English", "Subject", "Subjects"
}

def tokenize_visible_text(text: str):
    """Return list of English-like words, stripping numbers/punctuation; respects WHITELIST."""
    words = re.findall(r"[A-Za-z]{3,}", text or "")
    wl = {w.lower() for w in WHITELIST}
    # keep words but mark misspellings later; whitelist only affects 'miss' set
    return words, wl

def analyze_text(text: str):
    """Return (unique_words_sorted, misspelled_map) where misspelled_map[w] = suggestion."""
    speller = SpellChecker()
    words, whitelist = tokenize_visible_text(text)
    uniq = sorted({w for w in words}, key=lambda s: (s.lower(), s))
    # miss: exclude whitelisted words
    lowers = [w.lower() for w in uniq if w.lower() not in whitelist]
    miss = speller.unknown(lowers)
    miss_map = {}
    for w in uniq:
        wl = w.lower()
        if wl in miss:
            # best-effort single suggestion
            cand = next(iter(speller.candidates(wl)), None)
            miss_map[w] = cand
    return uniq, miss_map

def write_txt_report(path: str, page_title: str, url: str, words: list[str], miss_map: dict[str, str]):
    """Write a TXT report with All Words and Misspelled+suggestion sections."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = []
    lines.append(f"PAGE: {page_title}")
    lines.append(f"URL:   {url}")
    lines.append(f"TOTAL WORDS (unique): {len(words)}")
    lines.append(f"MISSPELLED COUNT: {len(miss_map)}")
    lines.append("")
    lines.append("== MISSPELLED WITH SUGGESTIONS ==")
    if miss_map:
        for w in sorted(miss_map, key=lambda s: s.lower()):
            lines.append(f"- {w} -> suggestion: {miss_map[w]}")
    else:
        lines.append("(none)")
    lines.append("")
    lines.append("== ALL WORDS SCANNED (UNIQUE) ==")
    if words:
        for w in words:
            lines.append(w)
    else:
        lines.append("(none)")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path
