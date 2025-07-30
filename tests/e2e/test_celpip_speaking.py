# tests/e2e/test_mp3_upload.py
import os
from pathlib import Path
from unittest.mock import patch
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .helpers import DjangoE2ETestCase
from playwright.sync_api import sync_playwright
import json
from django.utils import timezone
from datetime import timedelta
from api2d.models import Api2dGroup2ExpirationMapping, Api2dKey
from django.conf import settings
import pytest


@pytest.mark.e2e
class TestCelpipSpeaking(DjangoE2ETestCase):
    """Test MP3 file upload and transcription functionality."""

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

        # Create a test audio file if it doesn't exist
        self.test_dir = os.path.join(settings.MEDIA_ROOT, "test_uploads")
        self.test_audio_path = os.path.join(self.test_dir, "test_audio.mp3")
        os.makedirs(self.test_dir, exist_ok=True)
        if not os.path.exists(self.test_audio_path):
            with open(self.test_audio_path, "wb") as f:
                f.write(
                    b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
                )

        self.upload_url = reverse("api2d:celpip-speaking")

    def test_mp3_upload_flow(self):
        """Test the complete MP3 upload and transcription flow with external API."""
        with sync_playwright() as playwright:
            page = self.open(self.upload_url, playwright)

            # Enable request interception
            page.route(
                "**/v1/audio/transcriptions*",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(
                        {
                            "text": "This is a test transcription from the mock API",
                            "usage": {"final_total": 200},
                        }
                    ),
                ),
            )

            page.route(
                "**/dashboard/billing/credit_grants*",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({"total_available": 200, "total_granted": 200}),
                ),
            )
            # Below is the openai mock
            # page.route(
            #     "**/v1/chat/completions*",
            #     lambda route: route.fulfill(
            #         status=200,
            #         content_type="application/json",
            #         body=json.dumps(
            #             {
            #                 "choices": [
            #                     {
            #                         "message": {
            #                             "content": "This is a test chat completion from the mock API"
            #                         }
            #                     }
            #                 ],
            #             }
            #         ),
            #     ),
            # )
            # reload to let the patching work

            # Below is the claude mock
            page.route(
                "**/claude/v1/messages*",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(
                        {
                            "content": [
                                {
                                    "text": "<revised_text>This is a test revised text</revised_text><grammar_focused_feedback>Test feedback</grammar_focused_feedback>"
                                }
                            ],
                            "usage": {"final_total": 100},
                        }
                    ),
                ),
            )

            page.reload()

            try:
                self.take_screenshot("before_file_selection")

                # Wait for the upload tab button to be visible and clickable
                upload_tab_button = page.get_by_test_id("upload-tab-button")
                upload_tab_button.wait_for(
                    state="visible", timeout=10000
                )  # Wait up to 10 seconds

                # Click the button
                upload_tab_button.click()

                # Wait for the file input to be visible in the upload tab
                file_input = page.locator("#audioFile")
                file_input.wait_for(state="visible", timeout=10000)

                # Set the test file
                file_input.set_input_files(self.test_audio_path)
                # file_input.set_input_files('/home/haojie/django-user-app/tests/speech-to-txt-testing-file.M4A')

                # Wait for the audio player to be visible
                self.take_screenshot("after_file_selection")

                # wait a bit to let the fetch credit work
                page.wait_for_timeout(1000)

                self.take_screenshot("after_credit_fetch")

                # Click the submit button
                # page.click('form#audioUploadForm button[type="submit"]')
                page.get_by_test_id("submit-button").click()

                self.take_screenshot("after_submit")

                self.take_screenshot("after_transcription")
                # Verify the transcription using data-testid
                transcription_text = page.text_content(
                    '[data-testid="transcription-text"]'
                )
                self.assertIn("test transcription", transcription_text)

                # Verify improved text using data-testid
                improved_text = page.text_content('[data-testid="improved-text"]')
                self.assertIn("This is a test revised text", improved_text)

                # Verify suggestion text using data-testid
                suggestion_text = page.text_content('[data-testid="suggestion-text"]')
                self.assertIn("Test feedback", suggestion_text)

            except Exception as e:
                self.take_screenshot("mp3_upload_error")
                raise e
