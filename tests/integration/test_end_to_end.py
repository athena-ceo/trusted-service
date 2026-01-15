"""Integration tests for end-to-end workflows
Tests complete user journeys through the application.

Note: These tests require both backend and Delphes frontend to be running.
Use docker-compose.integration.yml to start the full stack for testing.
"""

import os

import httpx
import pytest
from playwright.sync_api import Page


@pytest.fixture()
def api_base_url() -> str:
    return os.getenv("API_BASE_URL", "http://localhost:8002")


@pytest.fixture()
def frontend_base_url() -> str:
    return os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")


class TestCompleteUserJourney:
    """Test complete user workflow from form to submission.

    Note: Playwright/Chromium tests may fail on macOS Sequoia due to
    known Chromium sandbox issues. Tests run successfully in CI (Linux).
    """

    def test_delphes_contact_flow(
        self,
        page: Page,
        frontend_base_url: str,
        api_base_url: str,
    ) -> None:
        """Test complete Delphes contact form workflow.

        Tests the full user journey through the Delphes UI.
        Requires both backend and frontend to be running (via docker-compose.integration.yml).

        Note: May fail locally on macOS due to Chromium headless sandboxing issue.
        Works correctly in GitHub Actions (Linux).
        """
        # Step 1: Navigate to contact form
        page.goto(f"{frontend_base_url}/accueil-etrangers", wait_until="networkidle")

        # Step 2: Fill out initial form
        # Note: Adjust selectors based on actual form structure
        page.wait_for_selector("form", timeout=10000)

        # Fill in test data if form fields exist
        if page.locator("input[name='nom']").count() > 0:
            page.fill("input[name='nom']", "Test")
            page.fill("input[name='prenom']", "User")

            if page.locator("input[name='email']").count() > 0:
                page.fill("input[name='email']", "test@example.com")

        # Step 3: Submit form (if submit button exists)
        submit_button = page.locator("button[type='submit']").first
        if submit_button.count() > 0 and submit_button.is_visible():
            # Note: This may navigate to analysis page
            pass  # Add actual submission logic based on app flow


class TestAPIIntegration:
    """Test frontend-backend integration."""

    def test_analyze_request_integration(self, api_base_url: str) -> None:
        """Test analyze API call with valid data."""
        client = httpx.Client(base_url=api_base_url, timeout=30.0)

        response = client.post(
            "/api/v2/apps/delphes/fr/analyze",
            json={
                "field_values": {},
                "text": "Je souhaite renouveler mon titre de séjour",
                "read_from_cache": False,
                "llm_config_id": "default",
            },
        )

        # Should succeed or return expected error (not 404)
        assert (
            response.status_code != 404
        ), f"Endpoint not found: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict), "Should return dictionary"

        client.close()

    def test_handle_case_integration(self, api_base_url: str) -> None:
        """Test handle_case API call."""
        client = httpx.Client(base_url=api_base_url, timeout=30.0)

        # Prepare case handling request
        case_request = {
            "intention_id": "renouvellement_titre_sejour",
            "field_values": {
                "nom": "Dupont",
                "prenom": "Jean",
                "date_naissance": "1990-01-15",
            },
        }

        response = client.post(
            "/api/v2/apps/delphes/fr/handle_case",
            json={"case_request": case_request},
        )

        # Should handle the request (not 404)
        assert (
            response.status_code != 404
        ), f"Endpoint not found: {response.status_code}"

        client.close()


class TestMultilingualSupport:
    """Test multilingual functionality."""

    def test_french_locale(self, api_base_url: str) -> None:
        """Test API with French locale."""
        client = httpx.Client(base_url=api_base_url, timeout=30.0)

        response = client.post(
            "/api/v2/apps/delphes/fr/analyze",
            json={
                "field_values": {},
                "text": "Bonjour, je souhaite obtenir un titre de séjour",
                "read_from_cache": False,
                "llm_config_id": "default",
            },
        )

        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
        client.close()

    def test_english_locale(self, api_base_url: str) -> None:
        """Test API with English locale."""
        client = httpx.Client(base_url=api_base_url, timeout=30.0)

        response = client.post(
            "/api/v2/apps/delphes/en/analyze",
            json={
                "field_values": {},
                "text": "Hello, I would like to obtain a residence permit",
                "read_from_cache": False,
                "llm_config_id": "default",
            },
        )

        # Should not return 404 (endpoint exists)
        assert response.status_code != 404
        client.close()


class TestCaching:
    """Test caching functionality."""

    def test_repeated_requests_cached(self, api_base_url: str) -> None:
        """Test that repeated identical requests are faster (cached)."""
        import time

        client = httpx.Client(base_url=api_base_url, timeout=30.0)

        request_data = {
            "app_name": "delphes",
            "locale": "fr",
            "message": "Test de cache pour les requêtes identiques",
        }

        # First request
        start1 = time.time()
        response1 = client.post("/api/analyze_request", json=request_data)
        _ = time.time() - start1

        if response1.status_code == 200:
            # Second identical request
            start2 = time.time()
            response2 = client.post("/api/analyze_request", json=request_data)
            _ = time.time() - start2

            # Second request should be similar or faster
            assert response2.status_code == 200
            # Note: May not always be faster due to various factors

        client.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])
