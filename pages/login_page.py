from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class LoginPage:
    USER_ID = (By.XPATH, "//input[@placeholder='User ID']")
    PASSWORD = (By.XPATH, "//input[@placeholder='Password']")
    SIGN_IN = (By.XPATH, "//button[normalize-space()='SIGN IN']")
    ACADEMICS = (By.XPATH, "//span[normalize-space()='Academics']")

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def open(self):
        self.driver.get(f"{self.base_url}/login")

    # ----- granular actions -----
    def set_user(self, user):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.USER_ID)).clear()
        self.driver.find_element(*self.USER_ID).send_keys(user)

    def set_password(self, password):
        WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.PASSWORD)).clear()
        self.driver.find_element(*self.PASSWORD).send_keys(password)

    def click_sign_in(self):
        self.driver.find_element(*self.SIGN_IN).click()

    def wait_logged_in(self):
        wait = WebDriverWait(self.driver, 20)
        try:
            wait.until(lambda d: "/login" not in d.current_url)
        except TimeoutException:
            pass
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.ACADEMICS))
        except TimeoutException:
            if "/login" in self.driver.current_url:
                raise

    # Backward compatible method
    def login(self, user, password):
        self.set_user(user)
        self.set_password(password)
        self.click_sign_in()
        self.wait_logged_in()

    def is_logged_in(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.ACADEMICS))
            return True
        except Exception:
            return False




