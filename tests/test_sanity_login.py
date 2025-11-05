import datetime
from pages.login_page import LoginPage

def test_login_sanity(driver, config, shots, report):
    lp = LoginPage(driver, config["base_url"])
    lp.open()
    shots.capture("Login Page Opened", "Initial login page")
    lp.login(config["user"], config["password"])
    assert lp.is_logged_in(), "Login did not reach dashboard/sidebar."
    shots.capture("Login Successful", "Sidebar visible indicates authenticated session")
    report.add_info(f"Logged in at {datetime.datetime.now().isoformat()} as {config['user']}")
