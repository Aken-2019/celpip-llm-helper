from playwright.sync_api import expect
from .helpers import DjangoE2ETestCase
from playwright.sync_api import sync_playwright
import pytest

@pytest.mark.e2e
class TestHomePage(DjangoE2ETestCase):
    """Test cases for the home page."""
    
    def test_homepage_loads(self):
        """Test that the home page loads successfully with expected content."""
        with self.settings(DEBUG=True):  # Enable debug for better error messages
            # Initialize Playwright
            
            with sync_playwright() as playwright:
                # Open the home page
                page = self.open('/', playwright)
                
                try:
                    # Verify page loaded
                    self.assert_page_loaded('/')
                    
                    # Check for important elements
                    expect(page.locator('body')).to_be_visible()
                    
                    # Example: Check for a specific heading (adjust selector as needed)
                    # expect(page.locator('h1')).to_contain_text('Welcome')
                    
                    # Take a screenshot for visual verification
                    self.take_screenshot('homepage')
                    
                except Exception as e:
                    # Save screenshot on failure
                    self.take_screenshot('homepage_error')
                    raise e

    def test_authenticated_user_flow(self):
        """Test authenticated user flow on the home page."""
        with self.settings(DEBUG=True):
            
            with sync_playwright() as playwright:
                # Open the home page
                page = self.open('/', playwright)
                
                try:
                    # If your app has a login form, you can test it like this:
                    # self.login()  # Uses the default test user
                    # expect(page.locator('.user-greeting')).to_contain_text(self.username)
                    
                    # Or if you need to test login through the UI:
                    # page.click('text=Login')
                    # page.fill('input[name="username"]', self.username)
                    # page.fill('input[name="password"]', self.password)
                    # page.click('button[type="submit"]')
                    # expect(page).to_have_url(f"{self.live_server_url}/")
                    
                    self.take_screenshot('authenticated_home')
                    
                except Exception as e:
                    self.take_screenshot('auth_flow_error')
                    raise e