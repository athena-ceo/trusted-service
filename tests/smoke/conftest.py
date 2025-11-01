"""
Pytest configuration for smoke tests
"""
import pytest

# Import Playwright only if available (needed for frontend tests only)
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@pytest.fixture(scope="session")
def browser_context_args():
    """Configure browser context for Playwright"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def page(browser_context_args):
    """Create a new browser page for each test"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not installed - skipping frontend tests")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        yield page
        context.close()
        browser.close()

