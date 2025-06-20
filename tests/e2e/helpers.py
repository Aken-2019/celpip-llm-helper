from django.contrib.staticfiles.testing import LiveServerTestCase
from django.contrib.auth import get_user_model
from django.test import Client
from playwright.sync_api import BrowserContext, Playwright, Page, expect
from django.conf import settings

User = get_user_model()


class DjangoE2ETestCase(LiveServerTestCase):
    """Base test case for end-to-end testing with Playwright."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()

    def setUp(self) -> None:
        """Set up test user and authentication."""
        self.username = "testuser"
        self.password = "testpass123"
        self.user = self.create_test_user()
        self.client.force_login(self.user)
        self.cookie = self.client.cookies["sessionid"]

    def create_test_user(self):
        """Create a test user if it doesn't exist and verify their email."""
        from allauth.account.models import EmailAddress

        user, created = User.objects.get_or_create(
            username=self.username,
            defaults={"email": "test@example.com", "is_active": True},
        )

        if created:
            user.set_password(self.password)
            user.save()

            # Ensure the email is verified
            EmailAddress.objects.get_or_create(
                user=user,
                email=user.email,
                defaults={"email": user.email, "verified": True, "primary": True},
            )

        return user

    def setup_browser(self, playwright: Playwright) -> BrowserContext:
        """Set up and return a browser context with authentication."""
        headless = getattr(settings, "PLAYWRIGHT_HEADLESS", True)
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()

        # Add session cookie for authentication
        context.add_cookies(
            [
                {
                    "name": "sessionid",
                    "value": self.cookie.value,
                    "domain": self.live_server_url.split("//")[-1].split(":")[0],
                    "path": "/",
                }
            ]
        )
        return context

    def open(self, url: str, playwright: Playwright) -> Page:
        """Open a URL in a new page with the authenticated browser context."""
        browser = self.setup_browser(playwright)
        self.page = browser.new_page()
        self.page.goto(f"{self.live_server_url}{url}")
        self.page.on("load", self.on_load)
        self.num_loads = 0
        return self.page

    def on_load(self):
        """Handle page load events."""
        if not hasattr(self, "num_loads"):
            self.num_loads = 0
        self.num_loads += 1

    def assert_page_loaded(self, url: str = None):
        """Assert that the page has loaded the expected URL."""
        if url:
            expect(self.page).to_have_url(f"{self.live_server_url}{url}")
        expect(self.page.locator("body")).to_be_visible()

    def login(self, email: str = None, password: str = None):
        """Helper method to log in through the UI using email."""
        email = email or getattr(self.user, "email", "test@example.com")
        password = password or self.password

        self.page.goto(f"{self.live_server_url}/accounts/login/")
        self.page.fill('input[name="login"]', email)
        self.page.fill('input[name="password"]', password)
        self.page.click('button[type="submit"]')
        self.page.wait_for_load_state(
            "networkidle"
        )  # Wait for any redirects to complete

    def navigate_to(self, menu_text: str, submenu_text: str = None):
        """Navigate through the application menu."""
        if submenu_text:
            self.page.get_by_role("button", name=menu_text).click()
            self.page.get_by_text(submenu_text, exact=True).click()
        else:
            self.page.get_by_text(menu_text, exact=True).click()

    def get_notification_message(self) -> str:
        """Get the text of the first notification message."""
        return self.page.locator(".messages .alert").first.text_content()

    def wait_for_loading(self, timeout: int = 5000):
        """Wait for loading indicators to disappear."""
        self.page.wait_for_selector(
            ".loading-indicator", state="hidden", timeout=timeout
        )

    def take_screenshot(self, name: str):
        """Take a screenshot and save it to the test-results directory."""
        import os

        os.makedirs("test-results", exist_ok=True)
        self.page.screenshot(path=f"test-results/{name}.png")

    def logout(self):
        """Log out the current user through the UI with confirmation."""
        try:
            self.page.goto(f"{self.live_server_url}/accounts/logout/")
            self.page.wait_for_selector('form[action*="logout"]', state="visible")
            # Submit the logout confirmation form
            self.page.get_by_role("button", name="Logout").click()
            # Wait for logout to complete
            self.page.wait_for_load_state("networkidle")
            # Verify we're logged out by checking for login link
            expect(self.page.get_by_role("link", name="Login")).to_be_visible()
        except Exception as e:
            self.take_screenshot("logout_error")
            raise Exception(f"Logout failed: {str(e)}")
