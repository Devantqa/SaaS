# tests/test_spelling_all_pages.py
import os
from pages.login_page import LoginPage
from utils.dom import get_visible_text
from utils.spell import analyze_text, write_txt_report

PAGES = [
    ("Login",   "/login"),
    ("Session", "/session"),
    ("Subject", "/subject"),
]

def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in name).strip("_")

def test_spelling_all_pages(driver, config, shots, report, report_pdf):
    os.makedirs("artifacts", exist_ok=True)
    summary_path = os.path.join("artifacts", "spelling_summary.txt")
    summary_lines = ["SPELLING SUMMARY", ""]

    # Login first
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    shots.capture("Spelling: Open login")
    lp.login(config["user"], config["password"])
    shots.capture("Spelling: Logged in")

    for title, route in PAGES:
        url = f"{config['base_url']}{route}"
        driver.get(url)
        shots.capture(f"Spelling: {title} page open")

        text = get_visible_text(driver)
        words, miss_map = analyze_text(text)

        out_txt = os.path.join("artifacts", f"spelling_{_slug(title)}.txt")
        write_txt_report(out_txt, title, url, words, miss_map)

        # Add to reports
        if miss_map:
            msg = f"{title}: {len(miss_map)} misspelled (see {os.path.basename(out_txt)})"
        else:
            msg = f"{title}: no spelling issues (see {os.path.basename(out_txt)})"
        report.add_info(msg)
        if report_pdf:
            report_pdf.add_step(f"Spelling - {title}", msg)

        # Add to summary
        summary_lines.append(msg)

    # Write combined summary
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("\n".join(summary_lines))
