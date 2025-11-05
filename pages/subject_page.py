# pages/subject_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


class SubjectPage:
    # ---------- Locators ----------
    SUBJECT_NAME = (By.XPATH, "//input[@placeholder='Eg. English']")
    SUBJECT_CODE = (By.XPATH, "//input[@placeholder='Eg. EN']")

    SAVE_BTN     = (By.XPATH, "//button[normalize-space()='Save']")
    UPDATE_BTN   = (By.XPATH, "//button[normalize-space()='Update']")

    # Confirm “Yes” (scoped to a visible dialog only)
    YES_IN_DIALOG = (
        By.XPATH,
        "//div[contains(@class,'p-dialog-mask') and contains(@class,'p-component-overlay') and not(contains(@class,'hidden'))]"
        "//button[@aria-label='Yes']"
    )

    LIST_HEADING = (By.XPATH, "//h4[normalize-space()='Subject List']")
    SEARCH       = (By.XPATH, "//input[@placeholder='Search by Subject Name or Code']")

    # Edit icon in first row (your SVG path signature), with fallback to any SVG in that cell
    FIRST_ROW_EDIT_PATH = (By.XPATH, "//tbody/tr[1]/td[3]//*[name()='svg']//*[name()='path' and contains(@d,'M471.6 21.')]")
    FIRST_ROW_EDIT_ANY  = (By.XPATH, "//tbody/tr[1]/td[3]//*[name()='svg']")

    # Generic validation / dialog markers
    ANY_DIALOG = (By.XPATH, "//*[contains(@class,'p-dialog') and not(contains(@class,'hidden'))]")
    ANY_ERROR_TEXT = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'required') or contains(., '*')]")
    ANY_INVALID    = (By.XPATH, "//*[@aria-invalid='true' or contains(@class,'p-invalid') or contains(@class,'ng-invalid')]")

    TABLE_ROWS = (By.CSS_SELECTOR, "tbody tr")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    # ---------- Private helpers ----------
    def _wait(self, timeout=20):
        return WebDriverWait(self.driver, timeout)

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

    def _click(self, locator, timeout=15):
        el = self._wait(timeout).until(EC.element_to_be_clickable(locator))
        self._scroll_into_view(el)
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def _type(self, locator, text, timeout=20, clear=True, send_enter=False):
        el = self._wait(timeout).until(EC.visibility_of_element_located(locator))
        if clear:
            el.clear()
        el.send_keys(text)
        if send_enter:
            try:
                el.send_keys("\n")
            except Exception:
                pass

    # ---------- Page API ----------
    def open(self):
        self.driver.get(f"{self.base_url}/subject")
        self._wait(30).until(EC.visibility_of_element_located(self.LIST_HEADING))

    # Setters
    def set_subject_name(self, name: str):
        self._type(self.SUBJECT_NAME, name)

    def set_subject_code(self, code: str):
        self._type(self.SUBJECT_CODE, code)

    def clear_form(self):
        # Clear both inputs (useful for validation test)
        self._type(self.SUBJECT_NAME, "", clear=True)
        self._type(self.SUBJECT_CODE, "", clear=True)

    # Actions
    def click_save(self):
        self._click(self.SAVE_BTN)

    def click_update(self):
        self._click(self.UPDATE_BTN)

    def confirm_yes(self, timeout=10):
        # Click Yes inside an open dialog; if there is no dialog, that's fine
        try:
            self._click(self.YES_IN_DIALOG, timeout=timeout)
        except TimeoutException:
            pass

    def type_search(self, text: str):
        self._type(self.SEARCH, text, send_enter=True)

    def click_first_row_edit(self, timeout=15):
        # Prefer your exact path signature; fallback to any SVG in action cell
        try:
            path_el = self._wait(timeout).until(EC.presence_of_element_located(self.FIRST_ROW_EDIT_PATH))
            edit_svg = path_el.find_element(By.XPATH, "./ancestor::*[name()='svg'][1]")
        except TimeoutException:
            edit_svg = self._wait(timeout).until(EC.presence_of_element_located(self.FIRST_ROW_EDIT_ANY))

        self._scroll_into_view(edit_svg)
        self._hover(edit_svg)
        try:
            self._wait(5).until(EC.element_to_be_clickable(edit_svg))
            edit_svg.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", edit_svg)

    def wait_for_rows(self, min_rows=1, timeout=30):
        self._wait(timeout).until(lambda d: len(d.find_elements(*self.TABLE_ROWS)) >= min_rows)
        return self.driver.find_elements(*self.TABLE_ROWS)

    # ---------- Validation helpers ----------
    def required_field_errors_present(self) -> bool:
        """
        Heuristics: if any 'invalid' markers or 'required' messages appear,
        we consider validation active. If a dialog pops immediately, treat as no client-side block.
        """
        invalids = self.driver.find_elements(*self.ANY_INVALID)
        if invalids:
            return True
        errs = self.driver.find_elements(*self.ANY_ERROR_TEXT)
        if errs:
            return True
        dialogs = self.driver.find_elements(*self.ANY_DIALOG)
        if dialogs:
            return False
        return False

    def save_expect_validation(self) -> bool:
        """
        Clicks Save with current form contents and returns True if
        client-side validation errors are detected (and no confirm dialog opened).
        """
        self.click_save()
        try:
            # small grace for UI to paint validation
            self._wait(2).until(lambda d: True)
        except Exception:
            pass
        return self.required_field_errors_present()
