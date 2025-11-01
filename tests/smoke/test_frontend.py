"""
Smoke tests for Frontend
These tests verify critical frontend pages load and function
Can be run locally or in CI/CD pipeline
"""
import pytest
import os
from playwright.sync_api import Page, expect


@pytest.fixture
def frontend_base_url() -> str:
    """Get frontend base URL from environment or use default"""
    return os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")


@pytest.fixture
def api_base_url() -> str:
    """Get API base URL from environment or use default"""
    return os.getenv("API_BASE_URL", "http://localhost:8002")


class TestFrontendPages:
    """Test critical frontend pages load"""
    
    def test_homepage_loads(self, page: Page, frontend_base_url: str):
        """Verify homepage loads successfully"""
        page.goto(frontend_base_url, wait_until="networkidle")
        
        # Should not show error page
        assert "error" not in page.url.lower()
        assert page.title(), "Page should have a title"
    
    def test_accueil_etrangers_page_loads(self, page: Page, frontend_base_url: str):
        """Verify main contact form page loads"""
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Check for form elements
        page.wait_for_selector("form", timeout=10000)
        
        # Verify key form fields exist
        assert page.locator("input[name='nom'], input[id='nom']").count() > 0, \
            "Last name field should exist"
    
    def test_dsfr_styles_loaded(self, page: Page, frontend_base_url: str):
        """Verify DSFR styles are loaded"""
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Check if DSFR classes are present
        dsfr_elements = page.locator("[class*='fr-']")
        assert dsfr_elements.count() > 0, "DSFR styles should be applied"


class TestFormFunctionality:
    """Test form functionality"""
    
    def test_form_fields_visible(self, page: Page, frontend_base_url: str):
        """Verify form fields are visible and interactive"""
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Wait for form to be ready
        page.wait_for_selector("form", timeout=10000)
        
        # Check that input fields are visible
        form = page.locator("form").first
        assert form.is_visible(), "Form should be visible"
    
    def test_form_validation(self, page: Page, frontend_base_url: str):
        """Test basic form validation"""
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Try to submit empty form
        submit_button = page.locator("button[type='submit']").first
        if submit_button.count() > 0:
            submit_button.click()
            
            # Should show validation messages or stay on page
            page.wait_for_timeout(1000)
            # Form should not navigate away immediately
            assert "accueil-etrangers" in page.url or "analysis" not in page.url


class TestAPIIntegration:
    """Test frontend-backend integration"""
    
    def test_api_proxy_works(self, page: Page, frontend_base_url: str):
        """Verify frontend can reach backend through proxy"""
        # Navigate to a page that makes API calls
        page.goto(frontend_base_url, wait_until="networkidle")
        
        # Check console for API errors
        console_errors = []
        page.on("console", lambda msg: 
            console_errors.append(msg.text) if msg.type == "error" else None)
        
        page.wait_for_timeout(2000)
        
        # Should not have critical API connection errors
        critical_errors = [e for e in console_errors if "ERR_CONNECTION_REFUSED" in e]
        assert len(critical_errors) == 0, f"API connection errors: {critical_errors}"


class TestAccessibility:
    """Test basic accessibility"""
    
    def test_page_has_proper_structure(self, page: Page, frontend_base_url: str):
        """Verify page has proper HTML structure"""
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Check for essential accessibility elements
        assert page.locator("html[lang]").count() > 0, "HTML should have lang attribute"
        assert page.locator("main").count() > 0, "Page should have main landmark"
    
    def test_form_labels(self, page: Page, frontend_base_url: str):
        """Verify form fields have proper labels"""
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Check that inputs have associated labels
        inputs = page.locator("input[type='text'], input[type='email']")
        count = inputs.count()
        
        if count > 0:
            # At least some inputs should have labels or aria-label
            labeled_inputs = page.locator(
                "input[aria-label], input[aria-labelledby], label input"
            )
            assert labeled_inputs.count() > 0, "Form inputs should have labels"


class TestPerformance:
    """Test frontend performance"""
    
    def test_page_loads_quickly(self, page: Page, frontend_base_url: str):
        """Verify page loads in reasonable time"""
        import time
        
        start = time.time()
        page.goto(frontend_base_url, wait_until="domcontentloaded")
        elapsed = time.time() - start
        
        assert elapsed < 5.0, f"Page took too long to load: {elapsed:.2f}s"
    
    def test_no_console_errors(self, page: Page, frontend_base_url: str):
        """Check for console errors on page load"""
        errors = []
        page.on("console", lambda msg: 
            errors.append(msg.text) if msg.type == "error" else None)
        
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        page.wait_for_timeout(2000)
        
        # Filter out known acceptable errors
        critical_errors = [e for e in errors 
                          if not any(skip in e for skip in ["favicon", "watson"])]
        
        assert len(critical_errors) == 0, f"Console errors found: {critical_errors}"


class TestResponsiveness:
    """Test responsive design"""
    
    def test_mobile_viewport(self, page: Page, frontend_base_url: str):
        """Verify page works on mobile viewport"""
        page.set_viewport_size({"width": 375, "height": 667})
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        # Page should still be functional
        form = page.locator("form").first
        assert form.is_visible(), "Form should be visible on mobile"
    
    def test_tablet_viewport(self, page: Page, frontend_base_url: str):
        """Verify page works on tablet viewport"""
        page.set_viewport_size({"width": 768, "height": 1024})
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")
        
        form = page.locator("form").first
        assert form.is_visible(), "Form should be visible on tablet"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])

