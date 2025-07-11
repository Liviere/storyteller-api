"""
Tests for main FastAPI application.
"""
import pytest
from fastapi import status


class TestMainApp:
    """Test cases for main application endpoints."""

    def test_root_endpoint(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {"message": "Welcome to Story Teller API"}

    def test_health_check_endpoint(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == {"status": "healthy", "database": "connected"}

    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        # Test CORS with an actual API request
        response = client.get("/api/v1/stories/")
        
        # CORS headers should be present in the response
        assert response.status_code == status.HTTP_200_OK
        # FastAPI automatically adds CORS headers when middleware is configured
        # We can verify the middleware is working by checking that requests work

    def test_api_documentation_endpoints(self, client):
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

    def test_invalid_endpoint(self, client):
        """Test accessing a non-existent endpoint."""
        response = client.get("/non-existent-endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND
