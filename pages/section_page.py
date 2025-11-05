# pages/section_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


class SectionPage:
    # ---------- Inputs / Selects ----------
    CLASS_SELECT    = (By.XPATH, "//select[@name='classId']")
    SECTION_NAME    = (By.XPATH, "//input[@placeholder='Eg. English']")
    SECTION_CODE    = (By.XPATH, "//input[@placeholder='Eg. EN']")
    SECTION_ORDER   = (By.XPATH, "//input[@placeholder='Eg. 1']")

    # ---------- Buttons ----------
    SAVE_BTN        = (By.XPATH, "//button[normalize-space()='Save']")
    UPDATE_BTN      = (By.XPATH, "//button[normalize-space()='Update']")
    YES_IN_DIALOG   = (
        By.XPATH,
        "//div[contains(@class,'p-dialog-mask') and contains(@class,'p-component-overlay') "
        "and not(contains(@class,'hidden'))]//button[@aria-label='Yes']"
    )

    # ---------- Page anchors / search ----------
    LIST_HEADING    = (By.XPATH, "//h4[contains(normalize-space(.),'Section List') or contains(normalize-space(.),'Sections')]")
    SEARCH          = (By.XPATH, "//input[@placeholder='Search by Section Name or Code']")

    # ---------- Table & Edit ----------
    TABLE_ROWS      = (By.CSS_SELECTOR, "tbody tr")
    FIRST_ROW       = (By.XPATH, "//tbody/tr[1]")
    FIRST_ROW_EDIT  = (By.XPATH, "//tbody/tr[1]/td[5]//*[name()='svg']")

    # ---------- Validation / dialog probes ----------
    ANY_DIALOG      = (By.XPATH, "//*[contains(@class,'p-dialog') and not(contains(@class,'hidden'))]")
    ANY_ERROR_TEXT  = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'required') or contains(., '*')]")
    ANY_INVALID     = (By.XPATH, "//*[@aria-invalid='true' or contains(@class,'p-invalid') or contains(@class,'ng-invalid')]")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    # ---------- Utils ----------
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

    def _type(self, locator, text, timeout=20, clear=True):
        el = self._wait(timeout).until(EC.visibility_of_element_located(locator))
        if clear:
            el.clear()
        el.send_keys(text)

    # ---------- Page API ----------
    def open(self):
        self.driver.get(f"{self.base_url}/section")
        self._wait(30).until(EC.visibility_of_element_located(self.LIST_HEADING))

    def select_class_by_visible_text(self, visible_text: str):
        sel_el = self._wait(15).until(EC.element_to_be_clickable(self.CLASS_SELECT))
        self._scroll_into_view(sel_el)
        Select(sel_el).select_by_visible_text(visible_text)

    def set_section_name(self, name: str):
        self._type(self.SECTION_NAME, name)

    def set_section_code(self, code: str):
        self._type(self.SECTION_CODE, code)

    def set_section_order(self, order_str: str):
        self._type(self.SECTION_ORDER, order_str)

    def click_save(self):
        self._click(self.SAVE_BTN)

    def click_update(self):
        self._click(self.UPDATE_BTN)

    def confirm_yes(self, timeout=10):
        try:
            self._click(self.YES_IN_DIALOG, timeout=timeout)
        except TimeoutException:
            pass

    def type_search(self, text: str):
        self._type(self.SEARCH, text, clear=True)

    def wait_for_rows(self, min_rows=1, timeout=30):
        self._wait(timeout).until(lambda d: len(d.find_elements(*self.TABLE_ROWS)) >= min_rows)
        return self.driver.find_elements(*self.TABLE_ROWS)

    def click_first_row_edit_and_confirm(self):
        # Ensure at least 1 row
        self.wait_for_rows(min_rows=1, timeout=30)
        # Click edit icon in action column
        edit_el = self._wait(10).until(EC.element_to_be_clickable(self.FIRST_ROW_EDIT))
        self._scroll_into_view(edit_el)
        self._hover(edit_el)
        try:
            edit_el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", edit_el)

        # dialog -> yes
        try:
            self._wait(10).until(EC.visibility_of_element_located(self.ANY_DIALOG))
            self.confirm_yes()
        except TimeoutException:
            pass

    # ---------- Validation helpers ----------
    def _touch_fields_to_trigger_validation(self):
        for loc in (self.SECTION_NAME, self.SECTION_CODE, self.SECTION_ORDER):
            try:
                el = self._wait(5).until(EC.visibility_of_element_located(loc))
                el.click()
            except Exception:
                pass
        self.driver.execute_script("document.activeElement && document.activeElement.blur && document.activeElement.blur();")

    def required_field_errors_present(self) -> bool:
        self._touch_fields_to_trigger_validation()
        if self.driver.find_elements(*self.ANY_INVALID):
            return True
        if self.driver.find_elements(*self.ANY_ERROR_TEXT):
            return True
        if self.driver.find_elements(*self.ANY_DIALOG):
            return False
        return False

    def save_expect_validation(self) -> bool:
        self.click_save()
        try:
            self._wait(2).until(lambda d: True)
        except Exception:
            pass
        return self.required_field_errors_present()
