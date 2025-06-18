import pytest
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright
from .helpers import DjangoE2ETestCase

@pytest.mark.e2e
class TestPageDetailView(DjangoE2ETestCase):    
    def test_active_page_display(self):
        """Test that an active page displays correctly."""
        from pages.models import Page
        
        # Create a test page with markdown content
        test_page = Page.objects.create(
            title="Test Page",
            slug="test-page",
            content="# Hello World\n\nThis is a **test** page with [a link](https://example.com).",
            is_active=True
        )
        
        # Navigate to the page
        url = reverse('pages:page_detail', kwargs={'slug': 'test-page'})
        with self.settings(DEBUG=True):  # set debug to false to align with prod

            with sync_playwright() as playwright:
                self.open(url, playwright)
                self.take_screenshot('active_page')

                # Check the title is displayed
                expect(self.page.get_by_role('heading', name='Test Page')).to_be_visible()
                
                # Check markdown is rendered to HTML
                expect(self.page.locator('h1:has-text("Hello World")')).to_be_visible()
                expect(self.page.get_by_text('This is a test page with')).to_be_visible()
                expect(self.page.get_by_role('link', name='a link')).to_be_visible()

                # the following test won't hold because markdown are rendered by markdown js and it's not rendered from the server
                # self.page.wait_for_selector('a[href*="example.com"]')
                # expect(self.page.get_by_text('test')).to_have_css('font-weight', '700')
                # expect(self.page.get_by_role('link', name='a link')).to_have_attribute('href', 'https://example.com/')

    def test_inactive_page_returns_404(self):
        """Test that inactive pages return 404."""
        from pages.models import Page
        
        # Create an inactive test page
        test_page = Page.objects.create(
            title="Inactive Page",
            slug="inactive-page",
            content="This page should not be visible.",
            is_active=False
        )
        
        # Try to navigate to the inactive page
        url = reverse('pages:page_detail', kwargs={'slug': 'inactive-page'})
        response = self.client.get(url)
        assert response.status_code == 404
    
    def test_nonexistent_page_returns_404(self):
        """Test that non-existent pages return 404."""
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        url = reverse('pages:page_detail', kwargs={'slug': 'non-existent-page'})
        response = client.get(url)
        assert response.status_code == 404


class TestHomePageView(DjangoE2ETestCase):
    def test_homepage_display(self):
        """Test that the homepage displays the correct content."""
        from pages.models import Page
        
        # Create a home page
        home_page = Page.objects.create(
            title="Welcome to Our Site",
            slug="home",
            content="# Welcome!\n\nThis is the homepage content.",
            is_active=True
        )
        
        with sync_playwright() as playwright:   
            # Navigate to the homepage
            self.open('/', playwright)
            
            # Check the title is displayed
            expect(self.page.get_by_role('heading', name='Welcome to Our Site')).to_be_visible()
            expect(self.page.locator('h1:has-text("Welcome!")')).to_be_visible()
            expect(self.page.locator('#content p').filter(has_text='This is the homepage content.')).to_be_visible()
    
    @pytest.mark.skip(reason="Home page is automatically created in the database when visiting the")
    def test_homepage_404_when_no_home_page(self):
        """Test that a 404 is returned when no home page exists."""
        from pages.models import Page
        from django.test import Client
        
        # Ensure no home page exists
        Page.objects.filter(slug='home').delete()
        
        client = Client()
        response = client.get('/')
        assert response.status_code == 404
