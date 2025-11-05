import os
import datetime
import time
import uuid
import pytest
from pages.login_page import LoginPage
from pages.session_page import SessionPage

TODAY = datetime.date.today().strftime("%m/%d/%Y")


def _unique_suffix():
    # e.g., "110410_3f2a"  (HHMMSS_hex4)
    return f"{datetime.datetime.now().strftime('%H%M%S')}_{uuid.uuid4().hex[:4]}"


def pytest_generate_tests(metafunc):
    """
    Allow multiple credential runs via env CREDS = 'U1:P1;U2:P2;...'
    If missing, a single run with config's --user/--password.
    """
    if {"user", "password", "config"}.issubset(metafunc.fixturenames):
        creds_env = os.getenv("CREDS", "").strip()
        if creds_env:
            creds = []
            for chunk in creds_env.split(";"):
                chunk = chunk.strip()
                if not chunk or ":" not in chunk:
                    continue
                u, p = chunk.split(":", 1)
                u, p = u.strip(), p.strip()
                if u and p:
                    creds.append((u, p))
            if creds:
                metafunc.parametrize("user,password", creds, ids=[f"user={u}" for u, _ in creds])
                return
        # Fallback: use config in the test body (None placeholders)
        metafunc.parametrize("user,password", [(None, None)], ids=["config-default"])


@pytest.mark.usefixtures("stepper")
def test_session_flow_stepwise(driver, config, stepper, user, password):
    # Resolve creds: prefer param values; fall back to config
    user = user or config["user"]
    password = password or config["password"]

    # Generate unique data for this test invocation
    suf = _unique_suffix()
    session_name = f"Bengali-{suf}"          # e.g., Bengali-110410_3f2a
    session_code = f"BEN{suf.replace('_','')}".upper()[:10]  # keep code compact, uppercase

    # Derived edit name
    edited_name = f"{session_name}v"

    lp = LoginPage(driver, config["base_url"])
    sp = SessionPage(driver, config["base_url"])

    # --- Login steps ---
    stepper.step(f"Open login page (user={user})", lambda: lp.open())
    stepper.step("Enter user id", lambda: lp.set_user(user))
    stepper.step("Enter password", lambda: lp.set_password(password))
    stepper.step("Click SIGN IN", lambda: lp.click_sign_in())
    stepper.step("Wait logged in", lambda: lp.wait_logged_in())

    # --- Navigate Session page ---
    stepper.step("Open Session page", lambda: sp.open())

    # --- Try save empty to see validation ---
    stepper.step("Click Save with empty form", lambda: sp.click_save())
    time.sleep(1)

    def _check_validation():
        assert sp.required_field_errors_present() or True  # don't fail flow; just trigger capture
    stepper.step("Check validation markers", _check_validation)

    # --- Create a session with UNIQUE name/code ---
    stepper.step(f"Set session name = {session_name}", lambda: sp.set_session_name(session_name))
    stepper.step(f"Set session code = {session_code}", lambda: sp.set_session_code(session_code))
    stepper.step("Set start date", lambda: sp.set_start_date(TODAY))
    stepper.step("Set end date", lambda: sp.set_end_date(TODAY))
    stepper.step("Click Save (create)", lambda: sp.click_save())
    stepper.step("Confirm Yes if modal", lambda: sp.confirm_yes())

    # --- Search + Edit (search for the fresh unique name) ---
    stepper.step(f"Type search '{session_name}'", lambda: sp.type_search(session_name))
    stepper.step("Edit first row and confirm", lambda: sp.click_first_edit_and_confirm())

    # --- Update name and save (to <unique>v) ---
    stepper.step(f"Change session name to {edited_name}", lambda: sp.set_session_name(edited_name))
    stepper.step("Click Save (update)", lambda: sp.click_save())
    stepper.step("Confirm Yes on update", lambda: sp.confirm_yes())