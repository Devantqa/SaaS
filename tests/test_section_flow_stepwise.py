# tests/test_section_flow_stepwise.py
from pages.login_page import LoginPage
from pages.section_page import SectionPage

def test_section_flow_stepwise(driver, config, stepper):
    lp = LoginPage(driver, config["base_url"])
    sp = SectionPage(driver, config["base_url"])

    # --- Login ---
    stepper.step("Open login page", lambda: lp.open())
    stepper.step("Enter user id", lambda: lp.set_user(config["user"]))
    stepper.step("Enter password", lambda: lp.set_password(config["password"]))
    stepper.step("Click SIGN IN", lambda: lp.click_sign_in())
    stepper.step("Wait logged in", lambda: lp.wait_logged_in())

    # --- Open Section page ---
    stepper.step("Open Section page", lambda: sp.open())

    # --- Validation: empty save must show errors ---
    def _empty_save():
        assert sp.save_expect_validation(), "Expected required-field validation on empty save."
    stepper.step("Validation: Save with empty form shows errors", _empty_save)

    # --- Create section ---
    stepper.step("Select Class 'X'", lambda: sp.select_class_by_visible_text("X"))
    stepper.step("Type Section Name 'History'", lambda: sp.set_section_name("History"))
    stepper.step("Type Section Code 'His'", lambda: sp.set_section_code("His"))
    stepper.step("Type Section Order '7'", lambda: sp.set_section_order("7"))
    stepper.step("Click Save", lambda: sp.click_save())
    stepper.step("Confirm Yes after Save", lambda: sp.confirm_yes())

    # --- Search and edit flow as specified ---
    stepper.step("Search 'Bengali'", lambda: sp.type_search("Bengali"))
    stepper.step("Wait for rows after search", lambda: sp.wait_for_rows(min_rows=1, timeout=30))
    stepper.step("Click Edit on first row", lambda: sp.click_first_row_edit_and_confirm())
    stepper.step("Confirm Yes after Edit", lambda: sp.confirm_yes())

    # --- Update name to Bengali1 & save ---
    stepper.step("Change Section Name to 'Bengali1'", lambda: sp.set_section_name("Bengali1"))
    stepper.step("Click Update", lambda: sp.click_update())
    stepper.step("Confirm Yes after Update", lambda: sp.confirm_yes())
