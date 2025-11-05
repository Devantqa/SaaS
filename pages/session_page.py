from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


class SessionPage:
    # ---------------- Inputs ----------------
    SESSION_NAME = (By.XPATH, "//input[@placeholder='Eg. 2025-2026']")
    SESSION_CODE = (By.XPATH, "//input[@placeholder='Eg. SN25']")
    START_DATE   = (By.XPATH, "//input[@name='startDate']")
    END_DATE     = (By.XPATH, "//input[@name='endDate']")

    # ---------------- Buttons (robust) ----------------
    # Save button candidates: primary is aria-label="Yes" per your update; include fallbacks.
    SAVE_CANDIDATES = [
        (By.XPATH, "//button[@aria-label='Yes']"),
        (By.XPATH, "//button[normalize-space()='Save']"),
        (By.XPATH, "//button[contains(@class,'p-button') and contains(.,'Save')]"),
        (By.CSS_SELECTOR, "button[type='submit']"),
    ]

    CANCEL_CANDIDATES = [
        (By.XPATH, "//button[normalize-space()='Cancel']"),
        (By.XPATH, "//button[contains(@class,'p-button') and contains(.,'Cancel')]"),
    ]

    # ---------------- Search & table ----------------
    SEARCH           = (By.XPATH, "//input[@placeholder='Eg. 2025-2026, SN25']")
    SESSION_LIST_HDR = (By.XPATH, "//h4[normalize-space()='Session List']")
    TABLE_ROWS       = (By.CSS_SELECTOR, "tbody tr")

    # Your specific edit icon locators (first row)
    FIRST_EDIT_ANY_SVG     = (By.XPATH, "//tbody/tr[1]/td[5]//*[name()='svg']")
    FIRST_EDIT_PATH_SIG    = (By.XPATH, "//tbody/tr[1]/td[5]//*[name()='svg']//*[name()='path' and contains(@d,'M471.6 21.')]")

    # ---------------- Dialogs ----------------
    # Full dialog mask you shared:
    EDIT_DIALOG = (By.XPATH, "//div[@class='p-dialog-mask p-dialog-center p-component-overlay p-component-overlay-enter p-dialog-resizable']")
    # Confirm “Yes” **scoped inside dialog only** (prevents hitting the Save button by mistake)
    CONFIRM_YES_IN_DIALOG = (By.XPATH, "//div[contains(@class,'p-dialog-mask') and contains(@class,'p-component-overlay') and not(contains(@class,'hidden'))]//button[@aria-label='Yes']")

    # Validation probes
    ANY_ERROR_TEXT = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'required') or contains(., '*')]")
    ANY_INVALID    = (By.XPATH, "//*[@aria-invalid='true' or contains(@class,'p-invalid') or contains(@class,'ng-invalid')]")
    ANY_DIALOG     = (By.XPATH, "//*[contains(@class,'p-dialog') and not(contains(@class,'hidden'))]")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    # ------------- Navigation -------------
    def open(self):
        self.driver.get(f"{self.base_url}/session")
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(self.SESSION_LIST_HDR))

    # ------------- Helpers -------------
    def _click_first(self, candidates, timeout_each=6):
        for by, sel in candidates:
            try:
                el = WebDriverWait(self.driver, timeout_each).until(EC.element_to_be_clickable((by, sel)))
                self._scroll_into_view(el)
                el.click()
                return True
            except Exception:
                continue
        return False

    def _scroll_into_view(self, el):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass

    def _hover(self, el):
        try:
            ActionChains(self.driver).move_to_element(el).perform()
        except Exception:
            pass

    # ------------- Setters -------------
    def set_session_name(self, name):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.SESSION_NAME)).clear()
        self.driver.find_element(*self.SESSION_NAME).send_keys(name)

    def set_session_code(self, code):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.SESSION_CODE)).clear()
        self.driver.find_element(*self.SESSION_CODE).send_keys(code)

    def set_start_date(self, start_date_str):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.START_DATE)).clear()
        self.driver.find_element(*self.START_DATE).send_keys(start_date_str)

    def set_end_date(self, end_date_str):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.END_DATE)).clear()
        self.driver.find_element(*self.END_DATE).send_keys(end_date_str)

    def click_save(self):
        # Try candidates; if none, JS fallback on the first selector
        if not self._click_first(self.SAVE_CANDIDATES):
            try:
                el = self.driver.find_element(*self.SAVE_CANDIDATES[0])
                self._scroll_into_view(el)
                self.driver.execute_script("arguments[0].click();", el)
            except Exception:
                raise TimeoutException("Could not locate/click any Save button candidate.")

    def click_cancel(self):
        if not self._click_first(self.CANCEL_CANDIDATES):
            try:
                el = self.driver.find_element(*self.CANCEL_CANDIDATES[0])
                self._scroll_into_view(el)
                self.driver.execute_script("arguments[0].click();", el)
            except Exception:
                raise TimeoutException("Could not locate/click any Cancel button candidate.")

    def fill_form(self, name, code, start_date, end_date):
        self.set_session_name(name)
        self.set_session_code(code)
        self.set_start_date(start_date)
        self.set_end_date(end_date)

    # ------------- Search & table -------------
    def type_search(self, text):
        el = self.driver.find_element(*self.SEARCH)
        el.clear()
        el.send_keys(text)
        try:
            el.send_keys("\n")  # if filter applies on Enter
        except Exception:
            pass

    def wait_for_rows(self, min_rows=1, timeout=30):
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(*self.TABLE_ROWS)) >= min_rows
        )
        return self.driver.find_elements(*self.TABLE_ROWS)

    # ------------- Edit flow (first row using your locators) -------------
    def click_first_edit_and_confirm(self, timeout=20):
        # Ensure table has at least one row
        self.wait_for_rows(min_rows=1, timeout=timeout)

        # Prefer the exact PATH signature
        try:
            edit_path = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.FIRST_EDIT_PATH_SIG)
            )
            edit_svg = edit_path.find_element(By.XPATH, "./ancestor::*[name()='svg'][1]")
        except TimeoutException:
            # Fallback: any SVG in the first row action cell
            edit_svg = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.FIRST_EDIT_ANY_SVG)
            )

        self._scroll_into_view(edit_svg)
        self._hover(edit_svg)
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(edit_svg))
            edit_svg.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", edit_svg)

        # Wait for your dialog; then click the dialog-scoped Yes (not the Save button)
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.EDIT_DIALOG))
            try:
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.CONFIRM_YES_IN_DIALOG)).click()
            except TimeoutException:
                pass
        except TimeoutException:
            # It's ok if no dialog appears; some UIs update inline
            pass

    # ------------- Dialog confirm helper -------------
    def confirm_yes(self):
        # Click 'Yes' **in dialog** (prevents ambiguity with Save)
        try:
            el = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.CONFIRM_YES_IN_DIALOG))
            self._scroll_into_view(el)
            el.click()
        except TimeoutException:
            # No dialog is fine
            pass

    # ------------- Validation helpers -------------
    def _touch_fields_to_trigger_validation(self):
        for loc in (self.SESSION_NAME, self.SESSION_CODE, self.START_DATE, self.END_DATE):
            try:
                el = WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(loc))
                el.click()
            except Exception:
                pass
        self.driver.execute_script(
            "document.activeElement && document.activeElement.blur && document.activeElement.blur();"
        )

    def required_field_errors_present(self):
        self._touch_fields_to_trigger_validation()
        if self.driver.find_elements(*self.ANY_INVALID):
            return True
        if self.driver.find_elements(*self.ANY_ERROR_TEXT):
            return True
        if self.driver.find_elements(*self.ANY_DIALOG):
            return False
        return False

