import os
from django.urls import reverse
from .helpers import DjangoE2ETestCase
from playwright.sync_api import sync_playwright
import json
from django.utils import timezone
from datetime import timedelta
from api2d.models import Api2dGroup2ExpirationMapping, Api2dKey
from django.conf import settings
import pytest


@pytest.mark.e2e
class TestCelpipWritingPage(DjangoE2ETestCase):
    def setUp(self):
        super().setUp()

        # Create a test user
        self.user = self.create_test_user()

        # Create a test group for API keys
        self.group = Api2dGroup2ExpirationMapping.objects.create(
            group="test-group", type_id="test-type", validate_days=30
        )

        # Create an API key for the test user
        self.api_key = Api2dKey.objects.create(
            key="test-api-key-123",
            user=self.user,
            group=self.group,
            expired_at=timezone.now() + timedelta(days=30),
        )

    def test_writing_page_display_and_submission(self):
        """Test that the Celpip Writing page loads and allows text submission."""
        # Navigate to the writing page
        url = reverse("api2d:celpip-writing")  # Update with your actual URL name
        with self.settings(DEBUG=True):
            with sync_playwright() as playwright:
                self.open(url, playwright)

                self.take_screenshot("celpip_writing_page_loaded")

                # Wait for the Svelte component to be loaded
                self.page.wait_for_selector('[data-svelte-component="celpipWritting"]')
                # Test input
                test_essay = "This is a test essay. It has some grammar issues that need to be fixed."
                # Find the textarea and type the test input
                textarea = self.page.locator("textarea")
                textarea.fill(test_essay)

    #             # Verify the input was entered correctly
    #             expect(textarea).to_have_value(test_essay)

    #             # Click the submit button
    #             submit_button = self.page.locator('button:has-text("提交")')
    #             submit_button.click()

    #             # Wait for loading to start
    #             expect(self.page.locator('.spinner-border')).to_be_visible()

    #             # Wait for the response (adjust timeout as needed)
    #             try:
    #                 # Wait for either the output to appear or an error message
    #                 response_locator = self.page.locator('.markdown-content')
    #                 response_locator.wait_for(state='visible', timeout=30000)  # 30 seconds timeout

    #                 # Verify we got some response
    #                 response_text = response_locator.inner_text()
    #                 assert len(response_text) > 0

    #                 # Take a screenshot of the result
    #                 self.take_screenshot("celpip_writing_response")

    #             except Exception as e:
    #                 # If there was an error, check for error message display
    #                 error_display = self.page.locator('.alert.alert-danger')
    #                 if error_display.is_visible():
    #                     error_text = error_display.inner_text()
    #                     pytest.fail(f"Error from application: {error_text}")
    #                 else:
    #                     raise e

    # def test_credit_display(self):
    #     """Test that credit information is displayed correctly."""
    #     url = reverse("celpip_writing")  # Update with your actual URL name
    #     with self.settings(DEBUG=True):
    #         with sync_playwright() as playwright:
    #             self.open(url, playwright)

    #             # Wait for the credit information to load
    #             try:
    #                 # This selector should match where credits are displayed in your UI
    #                 credits_display = self.page.locator('.badge.bg-warning')
    #                 credits_display.wait_for(state='visible', timeout=10000)

    #                 # Verify credits are displayed in the expected format
    #                 credits_text = credits_display.inner_text()
    #                 assert "剩余积分" in credits_text or "积分" in credits_text

    #             except Exception as e:
    #                 # If credits aren't visible, check if there's an error
    #                 error_display = self.page.locator('.alert.alert-danger')
    #                 if error_display.is_visible():
    #                     error_text = error_display.inner_text()
    #                     pytest.fail(f"Error loading credits: {error_text}")
    #                 else:
    #                     raise e
