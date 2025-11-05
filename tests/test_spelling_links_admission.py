# tests/test_spelling_links_admission.py
import re
import requests
from spellchecker import SpellChecker

from pages.login_page import LoginPage
from utils.dom import get_visible_text, collect_links

ALLOWED = {200, 204, 301, 302, 303, 307, 308}
TIMEOUT = 15

WHITELIST = {
    "Devant", "Admission", "Admissions", "Student", "Bengali",
    "XYZ", "abc", "VI", "T2", "T5", "English", "History",
    "SN25", "SHA", "SHT", "PN", "Dashboard", "Class", "Session",
    "Serial", "Certificate", "Transfer"
}

def _tokenize(text):
    words = re.findall(r"[A-Za-z]{3,}", text)
    wl = {w.lower() for w in WHITELIST}
    return [w for w in words if w.lower() not in wl]

def _check(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if r.status_code not in ALLOWED:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        return r.status_code in ALLOWED, r.status_code
    except Exception:
        return False, None

def test_spelling_and_links_on_admission(driver, config, shots, report_pdf, report_docx):
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    lp.login(config["user"], config["password"])
    shots.capture("Admission: Dashboard after login")

    # Scan /admission list page
    driver.get(f"{config['base_url']}/admission")
    shots.capture("Admission list open")
    text1 = get_visible_text(driver)

    # Click Add New Student and scan /studentAdmission page
    driver.get(f"{config['base_url']}/admission")
    shots.capture("Admission list (for link capture)")
    hrefs_list = collect_links(driver)

    # Open the form page itself too (in case the button is not clickable in headless)
    driver.get(f"{config['base_url']}/studentAdmission")
    shots.capture("Student Admission form open")
    text2 = get_visible_text(driver)
    hrefs_form = collect_links(driver)

    # Spelling analysis
    speller = SpellChecker()
    words = _tokenize(text1 + " " + text2)
    miss = speller.unknown([w.lower() for w in words])
    if miss:
        details = []
        for w in sorted(miss):
            cand = next(iter(speller.candidates(w)), None)
            details.append(f"{w} -> suggestion: {cand}")
        msg = "Admission pages spelling issues:\n" + "\n".join(details)
        report_docx.add_info(msg)
        report_pdf.add_info(msg)
    else:
        ok = "Admission pages: no spelling issues."
        report_docx.add_info(ok)
        report_pdf.add_info(ok)

    # Broken links check (both pages)
    bad = []
    for u in sorted(set(hrefs_list + hrefs_form)):
        ok, code = _check(u)
        if not ok:
            bad.append((u, code))
    if bad:
        shots.capture("Admission pages: Broken links")
        msg = "Admission pages broken links:\n" + "\n".join([f"{u} (status={code})" for u, code in bad])
        report_docx.add_info(msg)
        report_pdf.add_info(msg)
    else:
        ok = f"Admission pages: no broken links ({len(set(hrefs_list + hrefs_form))} links scanned)."
        report_docx.add_info(ok)
        report_pdf.add_info(ok)
