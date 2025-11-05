import os
import time
import pytest
from dotenv import load_dotenv

# Reports (PDF + DOCX)
from utils.report_pdf import PdfReport
from utils.report import DocxReport, ScreenshotHelper

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.event_firing_webdriver import (
    EventFiringWebDriver, AbstractEventListener
)
from webdriver_manager.chrome import ChromeDriverManager


# (Optional) Slow motion so you can watch steps
class SlowMoListener(AbstractEventListener):
    def __init__(self, delay_seconds: float):
        self.delay = max(0.0, float(delay_seconds or 0.0))
    def _sleep(self):
        if self.delay: time.sleep(self.delay)
    def before_click(self, element, driver): self._sleep()
    def before_change_value_of(self, element, driver): self._sleep()
    def before_navigate_to(self, url, driver): self._sleep()
    def before_find(self, by, value, driver): self._sleep()
    def after_execute_script(self, script, driver): self._sleep()


def pytest_addoption(parser):
    parser.addoption("--base-url", action="store", default=None, help="Base URL, e.g. https://school.devanttest.in")
    parser.addoption("--user", action="store", default=None, help="User ID")
    parser.addoption("--password", action="store", default=None, help="Password")
    parser.addoption("--headed", action="store_true", default=False, help="Run headed (not headless)")
    parser.addoption("--slowmo", action="store", default="0", help="Slow motion delay in seconds (e.g. 0.7)")


@pytest.fixture(scope="session")
def config(pytestconfig):
    load_dotenv()
    base_url = pytestconfig.getoption("--base-url") or os.getenv("BASE_URL", "https://school.devanttest.in")
    user     = pytestconfig.getoption("--user") or os.getenv("USER_ID", "SHA-PN-0001")
    password = pytestconfig.getoption("--password") or os.getenv("PASSWORD", "SHA-PN-0001")
    headed   = pytestconfig.getoption("--headed")
    slowmo   = float(pytestconfig.getoption("--slowmo") or 0)
    print(f"[pytest] CWD: {os.getcwd()}")
    print(f"[pytest] Artifacts dir: {os.path.join('artifacts')}")
    return {"base_url": base_url, "user": user, "password": password, "headed": headed, "slowmo": slowmo}


# --- Reports: build BOTH ---
@pytest.fixture(scope="session")
def report_pdf():
    r = PdfReport(out_path=os.path.join("artifacts", "TestSummary.pdf"))
    r.add_title("School Manager – Automated Test Report (PDF)")
    return r

@pytest.fixture(scope="session")
def report_docx():
    r = DocxReport(out_path=os.path.join("artifacts", "TestSummary.docx"))
    r.add_title("School Manager – Automated Test Report (DOCX)")
    return r

# Back-compat fixture so your tests using `report` continue working
@pytest.fixture
def report(report_docx):
    return report_docx


@pytest.fixture(scope="session", autouse=True)
def finalize_reports(report_pdf, report_docx):
    yield
    # Always save both reports
    os.makedirs("artifacts", exist_ok=True)
    try:
        report_pdf.save()
        print("[report] Saved PDF -> artifacts/TestSummary.pdf")
    except Exception as e:
        print(f"[report] PDF save error: {e}")
    try:
        report_docx.save()
        print("[report] Saved DOCX -> artifacts/TestSummary.docx")
    except Exception as e:
        print(f"[report] DOCX save error: {e}")


@pytest.fixture
def driver(config, report_pdf, report_docx):
    options = ChromeOptions()
    if not config["headed"]:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1440,900")
    options.add_argument("--disable-gpu")

    service = Service(ChromeDriverManager().install())
    drv = webdriver.Chrome(service=service, options=options)
    if config["slowmo"] and config["slowmo"] > 0:
        drv = EventFiringWebDriver(drv, SlowMoListener(config["slowmo"]))
    drv.set_page_load_timeout(60)
    yield drv
    drv.quit()


@pytest.fixture
def shots(driver, report_docx):
    # Screenshots embedded into DOCX; PDF will still log steps via the hook below
    return ScreenshotHelper(driver, report_docx)


# Screenshots on pass/fail + add a line to PDF for traceability
@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    shots = item.funcargs.get("shots")
    pdf = item.funcargs.get("report_pdf")
    if rep.when == "call":
        label = f"{item.name}_{int(time.time())}"
        status = "PASSED" if rep.passed else "FAILED"
        if pdf:
            pdf.add_step(f"{status}: {label}")
        if shots:
            shots.capture(f"{status}__{label}")
# --- Stepper fixture ---
from utils.stepper import Stepper

@pytest.fixture
def stepper(shots, report_pdf, report_docx):
    """
    Provides Stepper(shots, report_pdf, report_docx) to wrap each step.
    Usage:
        stepper.step("Open login", lambda: lp.open())
    """
    return Stepper(shots, report_pdf=report_pdf, report_docx=report_docx)