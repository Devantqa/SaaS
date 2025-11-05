import requests
from pages.login_page import LoginPage
from utils.dom import collect_links

TIMEOUT = 15
ALLOWED_STATUSES = {200, 204, 301, 302, 303, 307, 308}

def _check_url(url):
    try:
        # Use HEAD first; some servers require GET
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if r.status_code not in ALLOWED_STATUSES:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        return r.status_code in ALLOWED_STATUSES, r.status_code
    except Exception:
        return False, None

def test_broken_links_dashboard_and_session(driver, config, shots, report):
    # Login
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    lp.login(config["user"], config["password"])
    shots.capture("Links: Dashboard after login")

    # Scan dashboard
    dash_links = collect_links(driver)
    report.add_info(f"Dashboard links found: {len(dash_links)}")
    bad = []
    for u in dash_links:
        ok, code = _check_url(u)
        if not ok:
            bad.append((u, code))

    # Go to /session and scan there too
    driver.get(f"{config['base_url']}/session")
    shots.capture("Links: Session page open")
    sess_links = collect_links(driver)
    report.add_info(f"Session page links found: {len(sess_links)}")
    for u in sess_links:
        ok, code = _check_url(u)
        if not ok:
            bad.append((u, code))

    if bad:
        shots.capture("Broken Links Detected")
        report.add_info("Broken links:\n" + "\n".join([f"{u} (status={code})" for u, code in bad]))
    else:
        report.add_info("No broken links detected on scanned pages.")

