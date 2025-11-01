"""
Pytest configuration for smoke tests
"""
import pytest
from playwright.sync_api import sync_playwright


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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        yield page
        context.close()
        browser.close()

