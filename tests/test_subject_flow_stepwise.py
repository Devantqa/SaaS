# tests/test_subject_flow_stepwise.py
from pages.subject_page import SubjectPage
from pages.login_page import LoginPage

def test_subject_flow_stepwise(driver, config, stepper):
    lp = LoginPage(driver, config["base_url"])
    sp = SubjectPage(driver, config["base_url"])

    # --- Login ---
    stepper.step("Open login page", lambda: lp.open())
    stepper.step("Enter user id", lambda: lp.set_user(config["user"]))
    stepper.step("Enter password", lambda: lp.set_password(config["password"]))
    stepper.step("Click SIGN IN", lambda: lp.click_sign_in())
    stepper.step("Wait logged in", lambda: lp.wait_logged_in())

    # --- Open Subject page ---
    stepper.step("Open Subject page", lambda: sp.open())

    # --- VALIDATION: empty fields then Save should show required markers ---
    def _empty_save_validation():
        sp.clear_form()
        assert sp.save_expect_validation(), "Expected required-field validation on empty save."
    stepper.step("Validation: Save with empty form shows errors", _empty_save_validation)

    # --- Create subject (Name: bengali, Code: 12) ---
    stepper.step("Type Subject Name 'bengali'", lambda: sp.set_subject_name("bengali"))
    stepper.step("Type Subject Code '12'", lambda: sp.set_subject_code("12"))
    stepper.step("Click Save", lambda: sp.click_save())
    stepper.step("Confirm Yes after Save", lambda: sp.confirm_yes())

    # --- Search for the created record ---
    stepper.step("Search 'Bengali'", lambda: sp.type_search("Bengali"))
    stepper.step("Wait for filtered rows", lambda: sp.wait_for_rows(min_rows=1, timeout=30))

    # --- Edit first row and confirm ---
    stepper.step("Click Edit icon in first row", lambda: sp.click_first_row_edit())
    stepper.step("Confirm Yes after Edit", lambda: sp.confirm_yes())

    # --- Update Subject Name and save ---
    stepper.step("Change Subject Name to 'English1'", lambda: sp.set_subject_name("English1"))
    stepper.step("Click Update", lambda: sp.click_update())
    stepper.step("Confirm Yes after Update", lambda: sp.confirm_yes())

