from playwright.sync_api import expect
from django.test import override_settings
import pytest
from .helpers import DjangoE2ETestCase
from playwright.sync_api import sync_playwright

@pytest.mark.e2e
class TestLoginLogout(DjangoE2ETestCase):
    """Test login and logout functionality."""
    
    def test_authenticated_user_flow(self):
        """Test the complete login and logout flow."""
        with sync_playwright() as playwright:
            # Open the home page
            page = self.open('/', playwright)
            
            try:
                # First ensure we're logged out
                self.logout()
                self.take_screenshot('before_login')
                
                # Test login
                self.login()  # Uses the default test user
                expect(page.locator('#userDropdown')).to_contain_text(self.username)
                self.take_screenshot('after_login')
                
                # Test logout
                self.logout()
                expect(page.get_by_role('link', name='Login')).to_be_visible()
                self.take_screenshot('after_logout')
                
            except Exception as e:
                self.take_screenshot('auth_flow_error')
                raise e