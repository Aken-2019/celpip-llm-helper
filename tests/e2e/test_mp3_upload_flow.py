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

class TestMP3Upload(DjangoE2ETestCase):
    """Test MP3 file upload and transcription functionality."""
    
    def setUp(self):
        super().setUp()
        
        # Create a test user
        self.user = self.create_test_user()
        
        # Create a test group for API keys
        self.group = Api2dGroup2ExpirationMapping.objects.create(
            group="test-group",
            type_id="test-type",
            validate_days=30
        )
        
        # Create an API key for the test user
        self.api_key = Api2dKey.objects.create(
            key="test-api-key-123",
            user=self.user,
            group=self.group,
            expired_at=timezone.now() + timedelta(days=30)
        )
        
        # Create a test audio file if it doesn't exist
        self.test_dir = os.path.join(settings.MEDIA_ROOT, 'test_uploads')
        self.test_audio_path = os.path.join(self.test_dir, 'test_audio.mp3')
        os.makedirs(self.test_dir, exist_ok=True)
        if not os.path.exists(self.test_audio_path):
            with open(self.test_audio_path, 'wb') as f:
                f.write(b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')
        
        self.upload_url = reverse('api2d:celpip-speaking')

    def test_mp3_upload_flow(self):
        """Test the complete MP3 upload and transcription flow with external API."""
        with sync_playwright() as playwright:
            page = self.open(self.upload_url, playwright)
            
            # Enable request interception
            page.route('**/v1/audio/transcriptions*', lambda route: route.fulfill(
                status=200,
                content_type='application/json',
                body=json.dumps({
                    'text': 'This is a test transcription from the mock API',
                })
            ))

            page.route('**/dashboard/billing/credit_grants*', lambda route: route.fulfill(
                status=200,
                content_type='application/json',
                body=json.dumps({
                    'total_available': 200,
                    'total_granted': 200
                })
            ))
            
            page.route('**/v1/chat/completions*', lambda route: route.fulfill(
                status=200,
                content_type='application/json',
                body=json.dumps({
                    'choices': [{
                        'message': {
                            'content': 'This is a test chat completion from the mock API'
                        }
                    }],
                })
            ))
            # reload to let the patching work
            page.reload()

            try:
                self.take_screenshot('before_file_selection')
                # Wait for the form to be visible
                page.wait_for_selector('form#audioUploadForm', state='visible')

                # Set the test file
                file_input = page.locator('#audioFile')
                file_input.set_input_files(self.test_audio_path)
                # file_input.set_input_files('/home/haojie/django-user-app/tests/speech-to-txt-testing-file.M4A')
                
                # Manually trigger the change event
                page.evaluate('''() => {
                    const event = new Event('change', { bubbles: true });
                    document.querySelector('#audioFile').dispatchEvent(event);
                }''')

                # Wait for the audio player to be visible
                self.take_screenshot('after_file_selection')

                # wait a bit to let the fetch credit work
                page.wait_for_timeout(3000)

                self.take_screenshot('after_credit_fetch')


                # Click the submit button
                # page.click('form#audioUploadForm button[type="submit"]')
                page.get_by_role('button', name='开始润色与扩写').click()

                self.take_screenshot('after_submit')

                # Wait for the transcription text to update from the default value
                page.wait_for_function('''() => {
                    const el = document.querySelector('#transcriptionText');
                    return el && el.textContent !== '口语文字将会显示在这里...';
                }''')

                self.take_screenshot('after_transcription')
                # Verify the transcription
                transcription_text = page.text_content('#transcriptionText')
                self.assertIn('test transcription', transcription_text)

                improved_text = page.text_content('#wordCountAdvice')
                self.assertIn('test chat completion', improved_text)

                expanded_text = page.text_content('#elaborateTextContent')
                self.assertIn('test chat completion', expanded_text)


            except Exception as e:
                self.take_screenshot('mp3_upload_error')
                raise e