from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


class SessionPage:
    # =========================
    # Form inputs & actions
    # =========================
    SESSION_NAME = (By.XPATH, "//input[@placeholder='Eg. 2025-2026']")
    SESSION_CODE = (By.XPATH, "//input[@placeholder='Eg. SN25']")
    START_DATE   = (By.XPATH, "//input[@name='startDate']")
    END_DATE     = (By.XPATH, "//input[@name='endDate']")
    SAVE         = (By.XPATH, "//button[normalize-space()='Save']")
    CANCEL       = (By.XPATH, "//button[normalize-space()='Cancel']")

    # =========================
    # Search & table
    # =========================
    SEARCH           = (By.XPATH, "//input[@placeholder='Eg. 2025-2026, SN25']")
    SESSION_LIST_HDR = (By.XPATH, "//h4[normalize-space()='Session List']")
    TABLE_ROWS       = (By.CSS_SELECTOR, "tbody tr")

    # >>> Your exact edit locators (first-row action cell) <<<
    EDIT_BUTTON_ANY_SVG_FIRST_ROW = (By.XPATH, "//tbody/tr[1]/td[5]//*[name()='svg']")
    EDIT_BUTTON_PATH_SIGNATURE    = (By.XPATH, "//tbody/tr[1]/td[5]//*[name()='svg']//*[name()='path' and contains(@d,'M471.6 21.')]")

    # >>> Your exact dialog locator <<<
    EDIT_DIALOG = (By.XPATH, "//div[@class='p-dialog-mask p-dialog-center p-component-overlay p-component-overlay-enter p-dialog-resizable']")

    # We’ll still use the generic “Yes” for confirms (unchanged)
    CONFIRM_YES = (By.XPATH, "//button[@aria-label='Yes']")

    # Validation heuristics (unchanged)
    ANY_ERROR_TEXT = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'required') or contains(., '*')]")
    ANY_INVALID    = (By.XPATH, "//*[@aria-invalid='true' or contains(@class,'p-invalid') or contains(@class,'ng-invalid')]")
    ANY_DIALOG     = (By.XPATH, "//*[contains(@class,'p-dialog') and not(contains(@class,'hidden'))]")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    # -------------------- Navigation --------------------
    def open(self):
        self.driver.get(f"{self.base_url}/session")
        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(self.SESSION_LIST_HDR))

    # -------------------- Granular setters --------------------
    def set_session_name(self, name: str):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.SESSION_NAME)).clear()
        self.driver.find_element(*self.SESSION_NAME).send_keys(name)

    def set_session_code(self, code: str):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.SESSION_CODE)).clear()
        self.driver.find_element(*self.SESSION_CODE).send_keys(code)

    def set_start_date(self, start_date_str: str):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.START_DATE)).clear()
        self.driver.find_element(*self.START_DATE).send_keys(start_date_str)

    def set_end_date(self, end_date_str: str):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.END_DATE)).clear()
        self.driver.find_element(*self.END_DATE).send_keys(end_date_str)

    def click_save(self):
        self.driver.find_element(*self.SAVE).click()

    def click_cancel(self):
        self.driver.find_element(*self.CANCEL).click()

    def fill_form(self, name, code, start_date, end_date):
        self.set_session_name(name)
        self.set_session_code(code)
        self.set_start_date(start_date)
        self.set_end_date(end_date)

    # -------------------- Search & table helpers --------------------
    def type_search(self, text: str):
        el = self.driver.find_element(*self.SEARCH)
        el.clear()
        el.send_keys(text)
        try:
            el.send_keys("\n")  # some UIs filter on Enter
        except Exception:
            pass

    def wait_for_rows(self, min_rows: int = 1, timeout: int = 30):
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(*self.TABLE_ROWS)) >= min_rows
        )
        return self.driver.find_elements(*self.TABLE_ROWS)

    # -------------------- Edit flows (using your exact locators) --------------------
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

    def click_first_row_edit_icon(self, timeout: int = 20):
        """
        Click the edit icon in the first row using your exact SVG/path locators,
        wait for the dialog you specified, then click 'Yes' if present.
        """
        # Ensure at least one row exists
        self.wait_for_rows(min_rows=1, timeout=timeout)

        # Prefer the specific path signature if present
        try:
            edit_path = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.EDIT_BUTTON_PATH_SIGNATURE)
            )
            edit_svg = edit_path.find_element(By.XPATH, "./ancestor::*[name()='svg'][1]")
        except TimeoutException:
            # Fall back to "any SVG in first-row action cell"
            edit_svg = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.EDIT_BUTTON_ANY_SVG_FIRST_ROW)
            )

        # Scroll & hover to ensure it’s interactable
        self._scroll_into_view(edit_svg)
        self._hover(edit_svg)

        # Try to click (normal then JS fallback)
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(edit_svg))
            edit_svg.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", edit_svg)

        # Wait for the dialog you gave; then click "Yes" if visible
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.EDIT_DIALOG))
            try:
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.CONFIRM_YES)).click()
            except TimeoutException:
                # Some dialogs may auto-close or have no Yes button; that's ok
                pass
        except TimeoutException:
            # If that specific dialog isn’t used here, try the generic confirm (best-effort)
            try:
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(self.CONFIRM_YES)).click()
            except TimeoutException:
                pass

    # Backward-compatible helper name used in tests
    def click_first_edit_and_confirm(self, timeout: int = 20):
        self.click_first_row_edit_icon(timeout=timeout)

    def confirm_yes(self):
        try:
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(self.CONFIRM_YES)).click()
        except TimeoutException:
            pass  # If no confirm appears, that’s fine.

    # -------------------- Validation helpers --------------------
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

    def required_field_errors_present(self) -> bool:
        self._touch_fields_to_trigger_validation()
        if self.driver.find_elements(*self.ANY_INVALID):
            return True
        if self.driver.find_elements(*self.ANY_ERROR_TEXT):
            return True
        # If a dialog appears right after save, UI likely allowed submit (no client-side block)
        if self.driver.find_elements(*self.ANY_DIALOG):
            return False
        return False
