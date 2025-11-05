# tests/test_spelling_section.py
import re
from spellchecker import SpellChecker
from pages.login_page import LoginPage
from utils.dom import get_visible_text

WHITELIST = {
    "Devant", "Section", "Sections", "Bengali", "Bengali1", "History", "His", "XI", "XII",
    "SN25", "SHA", "SHT", "PN", "svg", "Dashboard", "Class", "Classes", "Session"
}

def _tokenize(text):
    words = re.findall(r"[A-Za-z]{3,}", text)
    wl = {w.lower() for w in WHITELIST}
    return [w for w in words if w.lower() not in wl]

def test_spelling_section(driver, config, shots, report_pdf, report_docx):
    speller = SpellChecker()

    lp = LoginPage(driver, config["base_url"])
    lp.open()
    lp.login(config["user"], config["password"])
    shots.capture("Spelling: Dashboard after login")

    # Scan Section page text
    driver.get(f"{config['base_url']}/section")
    shots.capture("Spelling: Section page open")
    text = get_visible_text(driver)
    words = _tokenize(text)
    miss = speller.unknown([w.lower() for w in words])

    if miss:
        details = []
        for w in sorted(miss):
            # one suggestion if available
            cand = next(iter(speller.candidates(w)), None)
            details.append(f"{w} -> suggestion: {cand}")
        msg = "Section page spelling issues:\n" + "\n".join(details)
        report_docx.add_info(msg)
        report_pdf.add_info(msg)
    else:
        ok = "Section page: no spelling issues detected."
        report_docx.add_info(ok)
        report_pdf.add_info(ok)
