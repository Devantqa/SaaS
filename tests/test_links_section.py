# tests/test_links_section.py
import requests
from pages.login_page import LoginPage
from utils.dom import collect_links

TIMEOUT = 15
ALLOWED = {200, 204, 301, 302, 303, 307, 308}

def _check(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if r.status_code not in ALLOWED:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        return r.status_code in ALLOWED, r.status_code
    except Exception:
        return False, None

def test_broken_links_section(driver, config, shots, report_pdf, report_docx):
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    lp.login(config["user"], config["password"])
    shots.capture("Links: Dashboard logged in")

    # Go to Section page
    driver.get(f"{config['base_url']}/section")
    shots.capture("Links: Section page open")

    hrefs = collect_links(driver)  # only same-origin by default
    bad = []
    for u in hrefs:
        ok, code = _check(u)
        if not ok:
            bad.append((u, code))

    if bad:
        shots.capture("Broken Links on Section page")
        msg = "Section page broken links:\n" + "\n".join([f"{u} (status={code})" for u, code in bad])
        report_docx.add_info(msg)
        report_pdf.add_info(msg)
    else:
        ok = f"Section page: no broken links ({len(hrefs)} links scanned)."
        report_docx.add_info(ok)
        report_pdf.add_info(ok)
