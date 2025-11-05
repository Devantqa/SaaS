# tests/test_class_spelling_links.py
import os
from pages.login_page import LoginPage
from utils.dom import get_visible_text, collect_links
from utils.spell import analyze_text, write_txt_report

def test_class_spelling_and_links(driver, config, shots, report, report_pdf):
    os.makedirs("artifacts", exist_ok=True)
    out_txt = os.path.join("artifacts", "spelling_class.txt")

    # Login
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    shots.capture("Class: Open login")
    lp.login(config["user"], config["password"])
    shots.capture("Class: Logged in")

    # Open /class
    url = f"{config['base_url']}/class"
    driver.get(url)
    shots.capture("Class: Page open")

    # Spelling
    text = get_visible_text(driver)
    words, miss_map = analyze_text(text)
    write_txt_report(out_txt, "Class", url, words, miss_map)
    msg = (f"/class spelling: {len(miss_map)} misspelled "
           f"(see {os.path.basename(out_txt)})")
    report.add_info(msg)
    if report_pdf:
        report_pdf.add_step("Spelling - Class", msg)

    # Broken links
    from tests.test_links_helpers import check_links  # see helper below
    bad = check_links(driver)
    if bad:
        report.add_info("Broken links on /class:\n" + "\n".join([f"{u} (status={code})" for u, code in bad]))
        shots.capture("Class: Broken links detected")
    else:
        report.add_info("No broken links detected on /class.")
        shots.capture("Class: No broken links")
