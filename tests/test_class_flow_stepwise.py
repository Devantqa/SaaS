# tests/test_class_flow_stepwise.py
from pages.login_page import LoginPage
from pages.class_page import ClassPage

def test_class_flow_stepwise(driver, config, stepper):
    lp = LoginPage(driver, config["base_url"])
    cp = ClassPage(driver, config["base_url"])

    # --- Login ---
    stepper.step("Open login page", lambda: lp.open())
    stepper.step("Enter user id", lambda: lp.set_user(config["user"]))
    stepper.step("Enter password", lambda: lp.set_password(config["password"]))
    stepper.step("Click SIGN IN", lambda: lp.click_sign_in())
    stepper.step("Wait logged in", lambda: lp.wait_logged_in())

    # --- Open Class page ---
    stepper.step("Open Class page", lambda: cp.open())

    # --- VALIDATION: empty form save should show required markers ---
    def _empty_save_validation():
        cp.clear_form()
        assert cp.save_expect_validation(), "Expected required-field validation on empty save."
    stepper.step("Validation: Save with empty form shows errors", _empty_save_validation)

    # --- Create: Name VI, Code 4, Order 6, Subject Science (CLICK-ONLY) ---
    stepper.step("Type Class Name 'VI'", lambda: cp.set_class_name("VI"))
    stepper.step("Type Class Code '4'", lambda: cp.set_class_code("4"))
    stepper.step("Type Class Order '6'", lambda: cp.set_class_order("6"))
    stepper.step("Select Subject 'Science' (click-only)", lambda: cp.select_science_click_only())
    stepper.step("Click Save", lambda: cp.click_save())
    stepper.step("Confirm Yes after Save", lambda: cp.confirm_yes())

    # --- Search for 'XI' as requested ---
    stepper.step("Search 'XI'", lambda: cp.type_search("XI"))
    stepper.step("Wait for filtered rows", lambda: cp.wait_for_rows(min_rows=1, timeout=30))

    # (Optional) log row count for debugging
    def _log_rows():
        print(f"[class] rows after filter = {cp.get_row_count()}")
    stepper.step("Log row count", _log_rows)

    # --- Edit row 3 safely (falls back to last row if <3 rows) ---
    stepper.step("Click Edit icon on row 3 (safe)", lambda: cp.click_edit_row_and_confirm(3))
    stepper.step("Confirm Yes after Edit (if modal)", lambda: cp.confirm_yes())

    # --- Update class name to 'XII' and save ---
    stepper.step("Change Class Name to 'XII'", lambda: cp.set_class_name("XII"))
    stepper.step("Click Update", lambda: cp.click_update())
    stepper.step("Confirm Yes after Update", lambda: cp.confirm_yes())

