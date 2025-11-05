# tests/test_admission_flow_stepwise.py
from pages.login_page import LoginPage
from pages.admission_page import AdmissionPage


def test_admission_flow_stepwise(driver, config, stepper):
    lp = LoginPage(driver, config["base_url"])
    ap = AdmissionPage(driver, config["base_url"])

    # -------- Login --------
    stepper.step("Open login page", lambda: lp.open())
    stepper.step("Enter user id", lambda: lp.set_user(config["user"]))
    stepper.step("Enter password", lambda: lp.set_password(config["password"]))
    stepper.step("Click SIGN IN", lambda: lp.click_sign_in())
    stepper.step("Wait logged in", lambda: lp.wait_logged_in())

    # -------- Admission page → New student form --------
    stepper.step("Open Admission page", lambda: ap.open_admission())
    stepper.step("Click 'Add New Student'", lambda: ap.click_add_new_student())

    # -------- Blank validation (open dropdown first, then Next) --------
    def _blank_validation():
        assert ap.next_expect_validation(), "Expected required-field validation when clicking Next on empty form."
    stepper.step("Blank Next → validation appears", _blank_validation)

    # -------- Fill base info --------
    stepper.step("Serial No = 20", lambda: ap.set_serial_no("20"))
    stepper.step("Admission Form No = 20", lambda: ap.set_admission_form_no("20"))
    stepper.step("Admission No = T2", lambda: ap.set_admission_no("T2"))

    # Class applied: open dropdown and select VI
    stepper.step("Open 'Class applied' dropdown", lambda: ap.open_class_applied_dropdown())
    stepper.step("Class Applied = VI", lambda: ap.select_class_applied("VI"))

    # Dates
    stepper.step("Form Date = today", lambda: ap.set_form_date_today())

    # Last School
    stepper.step("Last School Name = XYZ", lambda: ap.set_last_school_name("XYZ"))
    stepper.step("Last School Address = abc,123", lambda: ap.set_last_school_address("abc,123"))

    # Academics
    stepper.step("Second Language = Bengali", lambda: ap.set_second_language("Bengali"))
    stepper.step("TC Certificate No = T5", lambda: ap.set_tc_certificate_no("T5"))
    stepper.step("TC Date of Issue = today", lambda: ap.set_tc_date_today())

    # Last Result rows
    stepper.step("Add Last Result: English 100/80", lambda: ap.add_last_result_row("English", "100", "80"))
    stepper.step("Add Last Result: History 100/90", lambda: ap.add_last_result_row("History", "100", "90"))

    # Proceed
    stepper.step("Click Next →", lambda: ap.click_next())
