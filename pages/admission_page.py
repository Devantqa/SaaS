# pages/admission_page.py
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class AdmissionPage:
    # -------------------- Anchors / URLs --------------------
    STUDENT_MGMT_HDR = (By.XPATH, "//span[normalize-space()='Student Management']")
    ADD_NEW_STUDENT_BTN = (By.XPATH, "//button[normalize-space()='Add New Student']")
    STUDENT_ADMISSION_URL_PART = "studentAdmission"

    # -------------------- Admission form fields --------------------
    SERIAL_NO          = (By.XPATH, "//input[@name='serialNo']")
    ADMISSION_FORM_NO  = (By.XPATH, "//input[@name='admissionFormNo']")
    ADMISSION_NO       = (By.XPATH, "//input[@name='admissionNo']")

    CLASS_APPLIED_FIRST = (By.XPATH, "(//select[@name='classApplied'])[1]")   # open & select "VI"
    CLASS_APPLIED       = (By.XPATH, "//select[@name='classApplied']")

    FORM_DATE          = (By.XPATH, "//input[@name='formDate']")

    LAST_SCHOOL_NAME   = (By.XPATH, "//input[@name='lastSchool.name']")
    LAST_SCHOOL_ADDR   = (By.XPATH, "//input[@name='lastSchool.address']")

    # Academics → Second Language (tolerant to slight variations)
    SECOND_LANGUAGE    = (
        By.XPATH,
        "//input[@name='academics.secondLanguage' or @placeholder='Second Language' or @name='secondLanguage']"
    )

    TC_CERT_NO         = (By.XPATH, "//input[@name='academics.transferCertificate.certificateNo']")
    TC_DATE_ISSUE      = (By.XPATH, "//input[@name='academics.transferCertificate.dateOfIssue']")

    # -------------------- Last Result rows --------------------
    LR_SUBJECT         = (By.XPATH, "//input[@placeholder='Subject']")
    LR_MAX_MARKS       = (By.XPATH, "//input[@placeholder='Max Marks']")
    LR_OBTAINED        = (By.XPATH, "//input[@placeholder='Obtained']")
    LR_ADD_BTN         = (By.XPATH, "//button[@class='btn btn-success float-right']")  # green '+'

    # -------------------- Next button --------------------
    NEXT_BTN           = (By.XPATH, "//button[contains(text(),'Next →')]")
    NEXT_CANDIDATES    = [
        (By.XPATH, "//button[contains(text(),'Next →')]"),
        (By.XPATH, "//button[.//span[contains(normalize-space(),'Next')]]"),
        (By.XPATH, "//span[contains(normalize-space(),'Next')]/ancestor::button[1]"),
    ]

    # -------------------- Validation probes --------------------
    ANY_ERROR_TEXT = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'required') or contains(., '*')]")
    ANY_INVALID    = (By.XPATH, "//*[@aria-invalid='true' or contains(@class,'p-invalid') or contains(@class,'ng-invalid')]")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    # -------------------- Utils --------------------
    def _wait(self, timeout=20):
        return WebDriverWait(self.driver, timeout)

    def _scroll_into_view(self, el):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass

    def _scroll_doc_bottom(self):
        try:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass

    def _click(self, locator, timeout=10, allow_js=True):
        el = self._wait(timeout).until(EC.presence_of_element_located(locator))
        self._scroll_into_view(el)
        try:
            self._wait(timeout).until(EC.element_to_be_clickable(locator))
            el.click()
            return
        except Exception:
            if allow_js:
                try:
                    self.driver.execute_script("arguments[0].click();", el)
                    return
                except Exception:
                    pass
        # If not returned yet, raise
        self._wait(timeout).until(EC.element_to_be_clickable(locator))
        el.click()

    def _click_any(self, candidates, timeout_each=4):
        for by, sel in candidates:
            try:
                el = self._wait(timeout_each).until(EC.presence_of_element_located((by, sel)))
                self._scroll_into_view(el)
                try:
                    self._wait(timeout_each).until(EC.element_to_be_clickable((by, sel)))
                    el.click()
                    return True
                except Exception:
                    try:
                        self.driver.execute_script("arguments[0].click();", el)
                        return True
                    except Exception:
                        continue
            except Exception:
                continue
        return False

    def _type(self, locator, text, timeout=20, clear=True):
        el = self._wait(timeout).until(EC.visibility_of_element_located(locator))
        if clear:
            el.clear()
        el.send_keys(text)

    # -------------------- Navigation --------------------
    def open_admission(self):
        """Go to /admission and wait for 'Add New Student' button (and heading if present)."""
        self.driver.get(f"{self.base_url}/admission")
        # Wait for either the button or the heading
        self._wait(30).until(
            EC.any_of(
                EC.visibility_of_element_located(self.ADD_NEW_STUDENT_BTN),
                EC.visibility_of_element_located(self.STUDENT_MGMT_HDR)
            )
        )

    def click_add_new_student(self):
        """Click Add New Student and wait for /studentAdmission."""
        self._click(self.ADD_NEW_STUDENT_BTN, timeout=15)
        self._wait(20).until(EC.url_contains(self.STUDENT_ADMISSION_URL_PART))
        self._wait(20).until(EC.visibility_of_element_located(self.SERIAL_NO))

    # -------------------- Field setters --------------------
    def set_serial_no(self, value: str):
        self._type(self.SERIAL_NO, value)

    def set_admission_form_no(self, value: str):
        self._type(self.ADMISSION_FORM_NO, value)

    def set_admission_no(self, value: str):
        self._type(self.ADMISSION_NO, value)

    def open_class_applied_dropdown(self):
        """Explicitly open the Class applied dropdown first (as you requested)."""
        sel_el = self._wait(15).until(EC.element_to_be_clickable(self.CLASS_APPLIED_FIRST))
        try:
            sel_el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", sel_el)

    def select_class_applied(self, visible_text: str):
        sel_el = self._wait(15).until(EC.element_to_be_clickable(self.CLASS_APPLIED_FIRST))
        Select(sel_el).select_by_visible_text(visible_text)

    def set_form_date_today(self):
        today = datetime.date.today().strftime("%m/%d/%Y")
        self._type(self.FORM_DATE, today)

    def set_last_school_name(self, text: str):
        self._type(self.LAST_SCHOOL_NAME, text)

    def set_last_school_address(self, text: str):
        self._type(self.LAST_SCHOOL_ADDR, text)

    def set_second_language(self, text: str):
        self._type(self.SECOND_LANGUAGE, text)

    def set_tc_certificate_no(self, text: str):
        self._type(self.TC_CERT_NO, text)

    def set_tc_date_today(self):
        today = datetime.date.today().strftime("%m/%d/%Y")
        self._type(self.TC_DATE_ISSUE, today)

    # -------------------- Last Result rows --------------------
    def add_last_result_row(self, subject: str, max_marks: str, obtained: str):
        self._type(self.LR_SUBJECT, subject)
        self._type(self.LR_MAX_MARKS, max_marks)
        self._type(self.LR_OBTAINED, obtained)
        self._click(self.LR_ADD_BTN, timeout=10)

    # -------------------- Next --------------------
    def click_next(self):
        """Click the Next → button (scroll & try multiple candidates)."""
        self._scroll_doc_bottom()
        if self._click_any(self.NEXT_CANDIDATES, timeout_each=4):
            return
        self._click(self.NEXT_BTN, timeout=8)

    # -------------------- Validation --------------------
    def _touch_fields_to_trigger_validation(self):
        # Focus/blur likely required fields (esp. after opening class dropdown)
        for loc in (self.SERIAL_NO, self.ADMISSION_FORM_NO, self.ADMISSION_NO, self.CLASS_APPLIED_FIRST):
            try:
                el = self._wait(2).until(EC.visibility_of_element_located(loc))
                el.click()
            except Exception:
                continue
        try:
            self.driver.execute_script(
                "document.activeElement && document.activeElement.blur && document.activeElement.blur();"
            )
        except Exception:
            pass

    def _has_validation_indicators(self) -> bool:
        if self.driver.find_elements(*self.ANY_INVALID):
            return True
        if self.driver.find_elements(*self.ANY_ERROR_TEXT):
            return True
        return False

    def next_expect_validation(self) -> bool:
        """
        Check validation by:
          1) Opening the 'Class applied' dropdown first (as requested)
          2) Clicking Next →
          3) Surfacing any client-side messages and inspecting markers
        """
        try:
            self.open_class_applied_dropdown()
        except Exception:
            # If opening fails, continue; validators may still fire.
            pass

        try:
            self.click_next()
        except Exception:
            # If Next is disabled or not clickable yet, try to surface validators anyway.
            pass

        # Give the page a moment
        try:
            self._wait(1).until(lambda d: True)
        except Exception:
            pass

        self._touch_fields_to_trigger_validation()
        return self._has_validation_indicators()
