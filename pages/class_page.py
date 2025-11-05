# pages/class_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains


class ClassPage:
    # ---------- Form inputs ----------
    CLASS_NAME  = (By.XPATH, "//input[@placeholder='Eg. Class X']")
    CLASS_CODE  = (By.XPATH, "//input[@placeholder='Eg. CLS001']")
    CLASS_ORDER = (By.XPATH, "//input[@placeholder='Eg. 1']")

    # ---------- AntD subjects multiselect ----------
    SUBJECTS_DROPDOWN = (
        By.XPATH,
        "//div[contains(@class,'ant-select') and contains(@class,'ant-select-multiple')]"
        "//div[@class='ant-select-selection-overflow']"
    )

    # Your exact click target (NO typing/filtering)
    SCIENCE_OVERFLOW_CLICK = (
        By.XPATH,
        "//div[@class='ant-select-selection-overflow'][contains(.,'Science')]"
    )

    # Fallbacks: if Science renders inside AntD dropdown portal
    SUBJECT_OPTION_FALLBACKS = [
        (By.XPATH, "//div[contains(@class,'ant-select-dropdown')]//*[normalize-space()='Science']"),
        (By.XPATH, "//div[@role='listbox']//div[contains(@class,'ant-select-item-option-content') and normalize-space()='Science']"),
        (By.XPATH, "//div[@role='listbox']//div[contains(@class,'ant-select-item-option')][.//div[contains(@class,'ant-select-item-option-content') and normalize-space()='Science']]"),
    ]

    # Verify “Science” selected (chip or overflow text)
    SELECTED_CHIP_OR_OVERFLOW_SCIENCE = [
        (By.XPATH, "//span[contains(@class,'ant-select-selection-item') and (@title='Science' or normalize-space()='Science')]"),
        (By.XPATH, "//div[@class='ant-select-selection-overflow'][contains(.,'Science')]"),
    ]

    # ---------- Buttons ----------
    SAVE_BTN    = (By.XPATH, "//button[normalize-space()='Save']")
    UPDATE_BTN  = (By.XPATH, "//button[normalize-space()='Update']")

    # Confirm “Yes” scoped ONLY to visible dialog
    YES_IN_DIALOG = (
        By.XPATH,
        "//div[contains(@class,'p-dialog-mask') and contains(@class,'p-component-overlay') "
        "and not(contains(@class,'hidden'))]//button[@aria-label='Yes']"
    )

    # ---------- Page anchors / search ----------
    LIST_HEADING = (By.XPATH, "//h4[normalize-space()='Class List' or normalize-space()='Classes' or contains(.,'Class')]")
    SEARCH       = (By.XPATH, "//input[@placeholder='Search class...']")

    # ---------- Table ----------
    TABLE_ROWS   = (By.CSS_SELECTOR, "tbody tr")

    # Row / cell helpers
    def ROW(self, row_index: int):
        return (By.XPATH, f"//tbody/tr[{row_index}]")

    def ROW_ACTION_CELL(self, row_index: int):
        # action column is TD #4
        return (By.XPATH, f"//tbody/tr[{row_index}]/td[4]")

    # Your original exact path signature
    def EDIT_ICON_PATH_IN_ROW(self, row_index: int):
        return (By.XPATH, f"//tbody/tr[{row_index}]/td[4]//*[name()='svg']//*[name()='path' and contains(@d,'M471.6 21.')]")

    # Broader edit candidates
    def EDIT_ANY_SVG_IN_ROW(self, row_index: int):
        return (By.XPATH, f"//tbody/tr[{row_index}]/td[4]//*[name()='svg']")

    def EDIT_ANY_BUTTON_IN_ROW(self, row_index: int):
        # button/role=button containing 'edit' in text/title/aria-label
        return (By.XPATH, f"//tbody/tr[{row_index}]/td[4]//*[self::button or self::*[@role='button']][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit') or contains(translate(@title,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'edit')]")

    # ---------- Validation / dialog probes ----------
    ANY_DIALOG = (By.XPATH, "//*[contains(@class,'p-dialog') and not(contains(@class,'hidden'))]")
    ANY_ERROR_TEXT = (By.XPATH, "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'required') or contains(., '*')]")
    ANY_INVALID    = (By.XPATH, "//*[@aria-invalid='true' or contains(@class,'p-invalid') or contains(@class,'ng-invalid')]")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    # ---------- Utility ----------
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

    def _click_any(self, candidates, timeout_each=4):
        """Try multiple locators; return True on first successful click."""
        for by, sel in candidates:
            try:
                el = self._wait(timeout_each).until(EC.element_to_be_clickable((by, sel)))
                self._scroll_into_view(el)
                try:
                    el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", el)
                return True
            except Exception:
                continue
        return False

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

    def _try_click_element(self, el):
        self._scroll_into_view(el)
        try:
            self._hover(el)
        except Exception:
            pass
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def get_row_count(self) -> int:
        return len(self.driver.find_elements(*self.TABLE_ROWS))

    # ---------- Page API ----------
    def open(self):
        self.driver.get(f"{self.base_url}/class")
        self._wait(30).until(EC.visibility_of_element_located(self.LIST_HEADING))

    # Setters
    def set_class_name(self, name: str):
        self._type(self.CLASS_NAME, name)

    def set_class_code(self, code: str):
        self._type(self.CLASS_CODE, code)

    def set_class_order(self, order_str: str):
        self._type(self.CLASS_ORDER, order_str)

    def clear_form(self):
        self._type(self.CLASS_NAME, "", clear=True)
        self._type(self.CLASS_CODE, "", clear=True)
        self._type(self.CLASS_ORDER, "", clear=True)

    # ---------- Subjects: CLICK-ONLY selection of 'Science' ----------
    def select_science_click_only(self):
        """
        Open the Subjects multiselect and click the 'Science' element.
        No typing/filtering is performed.
        """
        # Open the control
        self._click(self.SUBJECTS_DROPDOWN, timeout=15)

        # Try your exact overflow XPath first
        try:
            el = self._wait(5).until(EC.presence_of_element_located(self.SCIENCE_OVERFLOW_CLICK))
            self._scroll_into_view(el)
            try:
                el.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", el)
        except TimeoutException:
            # Fallbacks: click from the ant-select dropdown/listbox
            clicked = self._click_any(self.SUBJECT_OPTION_FALLBACKS, timeout_each=4)
            if not clicked:
                raise TimeoutException("Could not find a clickable 'Science' option using provided XPath or fallbacks.")

        # Verify “Science” now appears in the control (chip or overflow text)
        ok = False
        for by, sel in self.SELECTED_CHIP_OR_OVERFLOW_SCIENCE:
            try:
                self._wait(5).until(EC.visibility_of_element_located((by, sel)))
                ok = True
                break
            except TimeoutException:
                continue
        if not ok:
            raise TimeoutException("Clicked 'Science' but did not detect it selected in the control.")

        # Optionally close dropdown
        try:
            self._click(self.SUBJECTS_DROPDOWN, timeout=3)
        except Exception:
            pass

    # ---------- Actions ----------
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
        self._type(self.SEARCH, text, send_enter=True)

    def wait_for_rows(self, min_rows=1, timeout=30):
        self._wait(timeout).until(lambda d: len(d.find_elements(*self.TABLE_ROWS)) >= min_rows)
        return self.driver.find_elements(*self.TABLE_ROWS)

    # ---------- Edit (safe index with fallbacks) ----------
    def click_edit_row_and_confirm(self, preferred_index: int = 3, timeout: int = 20):
        """
        Click the edit control for the given row index (1-based).
        If there are fewer rows than preferred_index, falls back to the last row.
        Tries multiple edit locators inside the action cell.
        """
        # Ensure there is at least one row
        rows = self.wait_for_rows(min_rows=1, timeout=timeout)
        total = len(rows)
        target_index = preferred_index if total >= preferred_index else total

        # Sanity: target row present
        self._wait(timeout).until(EC.presence_of_element_located(self.ROW(target_index)))

        # Try candidates in order: exact path, any svg, any edit button
        candidates = [
            self.EDIT_ICON_PATH_IN_ROW(target_index),
            self.EDIT_ANY_SVG_IN_ROW(target_index),
            self.EDIT_ANY_BUTTON_IN_ROW(target_index),
        ]

        clicked = False
        # Scope search to the action cell (faster & safer)
        action_cell = self._wait(timeout).until(EC.presence_of_element_located(self.ROW_ACTION_CELL(target_index)))
        for by, sel in candidates:
            try:
                el = action_cell.find_element(by, sel)
                self._try_click_element(el)
                clicked = True
                break
            except Exception:
                continue

        if not clicked:
            # As a last resort, search globally (DOM changes)
            for by, sel in candidates:
                try:
                    el = self._wait(3).until(EC.presence_of_element_located((by, sel)))
                    self._try_click_element(el)
                    clicked = True
                    break
                except Exception:
                    continue

        if not clicked:
            raise TimeoutException(f"Could not find a clickable edit control on row {target_index} (rows present: {total}).")

        # Wait for dialog, then confirm Yes (some builds may inline-edit without modal)
        try:
            self._wait(10).until(EC.visibility_of_element_located(self.ANY_DIALOG))
            self.confirm_yes()
        except TimeoutException:
            # No modal appeared; likely inline edit — that's okay
            return

    # ---------- Validation ----------
    def required_field_errors_present(self) -> bool:
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

