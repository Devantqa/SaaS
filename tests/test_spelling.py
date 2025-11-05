import os
import re
from spellchecker import SpellChecker
from pages.login_page import LoginPage
from utils.dom import get_visible_text

# Words to ignore (project/domain vocab, codes, names)
WHITELIST = {
    "Devant", "SN25", "SHT", "SHA", "PN", "Ben1234", "Bengali",
    "SRU", "WhatsApp", "Kiwi", "Academics", "Signin", "svg",
    "Dashboard", "Session", "Sessions", "Check", "Checkingv"
}

def _tokenize_english_words(text):
    words = re.findall(r"[A-Za-z]{3,}", text)
    wl = {x.lower() for x in WHITELIST}
    return [w for w in words if w.lower() not in wl]

def test_spelling_dashboard_and_session(driver, config, shots, report, report_pdf):
    speller = SpellChecker()
    os.makedirs("artifacts", exist_ok=True)
    out_txt = os.path.join("artifacts", "spelling_report.txt")

    # Login
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    lp.login(config["user"], config["password"])
    shots.capture("Spelling: Dashboard open")
    text = get_visible_text(driver)
    words = _tokenize_english_words(text)
    miss = speller.unknown([w.lower() for w in words])

    # Session page
    driver.get(f"{config['base_url']}/session")
    shots.capture("Spelling: Session open")
    text2 = get_visible_text(driver)
    words2 = _tokenize_english_words(text2)
    miss |= speller.unknown([w.lower() for w in words2])

    # Prepare results
    lines = []
    if miss:
        lines.append("Misspelled words and suggestions:\n")
        for w in sorted(miss):
            suggestion = next(iter(speller.candidates(w)), None)
            lines.append(f"- {w} -> suggestion: {suggestion}")
        report.add_info("Spelling issues found:\n" + "\n".join(lines[1:]))
        if report_pdf:
            report_pdf.add_step("Spelling issues found", "\n".join(lines[1:]))
    else:
        lines.append("No spelling issues detected.")
        report.add_info("No spelling issues detected on scanned pages.")
        if report_pdf:
            report_pdf.add_step("No spelling issues detected")

    # Write TXT file
    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))



