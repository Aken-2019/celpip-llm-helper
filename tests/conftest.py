import pytest
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def collectstatic():
    """Run collectstatic before all tests."""
    call_command("collectstatic", "--noinput", "--clear")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def authenticated_page(live_server, browser):
    # Create a new browser context and page for each test
    context = browser.new_context()
    page = context.new_page()

    # Here you can add authentication logic if needed
    # For example, if using Django's built-in authentication:
    # page.goto(f"{live_server.url}/admin/login/")
    # page.fill("#id_username", "admin")
    # page.fill("#id_password", "password")
    # page.click("button[type='submit']")

    yield page

    # Cleanup
    page.close()
    context.close()


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": True,  # Set to False for debugging
        "slow_mo": 0,  # Slow down execution by X ms
    }
