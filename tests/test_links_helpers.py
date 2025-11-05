# tests/test_links_helpers.py
import requests
from utils.dom import collect_links

TIMEOUT = 15
ALLOWED_STATUSES = {200, 204, 301, 302, 303, 307, 308}

def _check_url(url):
    try:
        r = requests.head(url, allow_redirects=True, timeout=TIMEOUT)
        if r.status_code not in ALLOWED_STATUSES:
            r = requests.get(url, allow_redirects=True, timeout=TIMEOUT)
        return r.status_code in ALLOWED_STATUSES, r.status_code
    except Exception:
        return False, None

def check_links(driver):
    links = collect_links(driver)
    bad = []
    for u in links:
        ok, code = _check_url(u)
        if not ok:
            bad.append((u, code))
    return bad
