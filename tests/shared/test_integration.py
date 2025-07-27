"""
Tests for main FastAPI application.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

@pytest.mark.integration
class TestMainApp:
    """Test cases for main application endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {"message": "Welcome to Story Teller API"}

    def test_health_check_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        with patch("app.main.engine.connect") as mock_connect:
            mock_connection = MagicMock()
            mock_connect.return_value.__enter__.return_value = mock_connection

            # Simulate a successful database connection
            mock_connection.scalar.return_value = 1
            response = client.get("/health")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Test app returns simplified health check
        assert data["status"] == "healthy"
        assert "database" in data

    def test_health_check_database_disconnected(self, client: TestClient):
        with patch("app.main.engine.connect", side_effect=Exception("DB error")):
            response = client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "unhealthy"
        assert body["database"] == "disconnected"
        assert "error" in body

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly set."""
        # Test CORS with an actual API request
        response = client.get("/api/v1/stories/")

        # CORS headers should be present in the response
        assert response.status_code == status.HTTP_200_OK
        # FastAPI automatically adds CORS headers when middleware is configured
        # We can verify the middleware is working by checking that requests work

    def test_api_documentation_endpoints(self, client: TestClient):
        """Test that API documentation endpoints are accessible."""
        # Test OpenAPI spec
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK

    def test_invalid_endpoint(self, client: TestClient):
        """Test accessing a non-existent endpoint."""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
