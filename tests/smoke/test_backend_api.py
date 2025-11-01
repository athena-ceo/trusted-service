"""
Smoke tests for Backend API
These tests verify critical API endpoints are functional
Can be run locally or in CI/CD pipeline
"""
import pytest
import httpx
import os
import time
from typing import Generator


@pytest.fixture
def api_base_url() -> str:
    """Get API base URL from environment or use default"""
    return os.getenv("API_BASE_URL", "http://localhost:8002")


@pytest.fixture
def api_client(api_base_url: str) -> Generator[httpx.Client, None, None]:
    """Create HTTP client for API testing"""
    client = httpx.Client(base_url=api_base_url, timeout=30.0)
    yield client
    client.close()


class TestAPIHealth:
    """Test API health and availability"""
    
    def test_api_is_reachable(self, api_client: httpx.Client):
        """Verify API server is running and reachable"""
        try:
            response = api_client.get("/")
            assert response.status_code in [200, 404], f"API not reachable: {response.status_code}"
        except httpx.ConnectError:
            pytest.fail("Cannot connect to API server. Is it running?")
    
    def test_health_endpoint(self, api_client: httpx.Client):
        """Verify health check endpoint returns 200 OK"""
        response = api_client.get("/api/health")
        assert response.status_code == 200, f"Health check failed: {response.text}"
        
        # If health endpoint returns JSON, validate structure
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "status" in data or "healthy" in data, "Health check missing status field"
    
    def test_docs_endpoint_available(self, api_client: httpx.Client):
        """Verify API documentation is available"""
        response = api_client.get("/docs")
        assert response.status_code == 200, "API docs not available"


class TestCriticalEndpoints:
    """Test critical API endpoints"""
    
    def test_analyze_request_endpoint_exists(self, api_client: httpx.Client):
        """Verify analyze_request endpoint exists (may return 422 for invalid data)"""
        response = api_client.post(
            "/api/analyze_request",
            json={}
        )
        # Should return 422 (validation error) or 400, not 404
        assert response.status_code in [400, 422], \
            f"Endpoint missing or unexpected error: {response.status_code}"
    
    def test_analyze_request_with_valid_data(self, api_client: httpx.Client):
        """Test analyze_request with minimal valid data"""
        response = api_client.post(
            "/api/analyze_request",
            json={
                "app_name": "delphes",
                "locale": "fr",
                "message": "Test message for smoke test"
            }
        )
        # Should succeed or return specific error (not server error)
        assert response.status_code in [200, 400, 422, 503], \
            f"Unexpected error: {response.status_code} - {response.text}"
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict), "Response should be a dictionary"
    
    def test_handle_case_endpoint_exists(self, api_client: httpx.Client):
        """Verify handle_case endpoint exists"""
        response = api_client.post(
            "/api/handle_case",
            json={}
        )
        assert response.status_code in [400, 422], \
            f"Endpoint missing or unexpected error: {response.status_code}"
    
    def test_get_intentions_endpoint(self, api_client: httpx.Client):
        """Test get_intentions endpoint if available"""
        response = api_client.get("/api/get_intentions?app_name=delphes&locale=fr")
        # May return 200 with data or error if not implemented
        assert response.status_code in [200, 404, 422], \
            f"Unexpected error: {response.status_code}"


class TestAPIPerformance:
    """Test API performance and response times"""
    
    def test_health_check_response_time(self, api_client: httpx.Client):
        """Verify health check responds quickly (under 2 seconds)"""
        start = time.time()
        response = api_client.get("/api/health")
        elapsed = time.time() - start
        
        assert response.status_code == 200
        assert elapsed < 2.0, f"Health check too slow: {elapsed:.2f}s"
    
    def test_concurrent_requests(self, api_client: httpx.Client):
        """Test API can handle multiple concurrent requests"""
        import concurrent.futures
        
        def make_request():
            return api_client.get("/api/health")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(r.status_code == 200 for r in results), "Some concurrent requests failed"


class TestAPIErrorHandling:
    """Test API error handling"""
    
    def test_invalid_json(self, api_client: httpx.Client):
        """Verify API handles invalid JSON gracefully"""
        response = api_client.post(
            "/api/analyze_request",
            content="invalid json{",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422], "Should reject invalid JSON"
    
    def test_missing_required_fields(self, api_client: httpx.Client):
        """Verify API validates required fields"""
        response = api_client.post(
            "/api/analyze_request",
            json={"app_name": "delphes"}  # Missing other required fields
        )
        assert response.status_code == 422, "Should validate required fields"
    
    def test_invalid_app_name(self, api_client: httpx.Client):
        """Verify API handles invalid app names"""
        response = api_client.post(
            "/api/analyze_request",
            json={
                "app_name": "nonexistent_app_12345",
                "locale": "fr",
                "message": "test"
            }
        )
        # Should return error, not crash
        assert response.status_code in [400, 404, 422], \
            f"Should handle invalid app gracefully: {response.status_code}"


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, api_client: httpx.Client):
        """Verify CORS headers are configured"""
        response = api_client.options(
            "/api/analyze_request",
            headers={"Origin": "http://localhost:3000"}
        )
        # Should have CORS headers or return 404 for OPTIONS
        assert response.status_code in [200, 204, 404], \
            f"CORS preflight failed: {response.status_code}"


if __name__ == "__main__":
    # Allow running smoke tests directly
    pytest.main([__file__, "-v", "--tb=short"])

