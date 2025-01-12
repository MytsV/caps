from lib.core.feature_descriptor import BaseFeatureDescriptor
from lib.infrastructure.fastapi.fastapi_endpoint import FastAPICrudRepositoryEndpoint
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.repository.models import TestSetup


class TestFastAPICrudRepositoryEndpoint(TestSetup):
    @pytest.fixture
    def app(self):
        return FastAPI()

    @pytest.fixture
    def test_client(self, app, endpoint):
        router = endpoint.load()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def descriptor(self):
        return BaseFeatureDescriptor(
            name="test-items",
            description="Test CRUD operations for items",
            version="1.0.0",
            tags=["test", "crud"],
            enabled=True,
            auth=True,
        )

    @pytest.fixture
    def responses(self):
        return {
            400: {"description": "Validation Error"},
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Not Found"},
            500: {"description": "Internal Server Error"},
        }

    @pytest.fixture
    def endpoint(self, repository, descriptor, responses):
        return FastAPICrudRepositoryEndpoint(repository=repository, descriptor=descriptor, responses=responses)

    @pytest.fixture
    def auth_headers(self):
        return {"X-Auth-Token": "test123"}

    def test_create_endpoint_success(self, test_client, auth_headers):
        response = test_client.post(
            "/api/v1/repository/test-items", json={"data": {"name": "New Item"}}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["data"]["name"] == "New Item"
        assert isinstance(data["data"]["data"]["id"], int)
        assert "created_at" in data["data"]

    def test_get_endpoint_success(self, test_client, auth_headers):
        create_response = test_client.post(
            "/api/v1/repository/test-items", json={"data": {"name": "Test Item"}}, headers=auth_headers
        )
        created_id = create_response.json()["data"]["data"]["id"]

        response = test_client.get(f"/api/v1/repository/test-items/{created_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Test Item"
        assert data["data"]["id"] == created_id

    def test_get_endpoint_not_found(self, test_client, auth_headers):
        response = test_client.get("/api/v1/repository/test-items/999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()["detail"]
        assert data["errorType"] == "not_found"

    def test_list_endpoint_success(self, test_client, auth_headers):
        test_client.post("/api/v1/repository/test-items", json={"data": {"name": "Item 1"}}, headers=auth_headers)
        test_client.post("/api/v1/repository/test-items", json={"data": {"name": "Item 2"}}, headers=auth_headers)

        response = test_client.get("/api/v1/repository/test-items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        names = {item["name"] for item in data["data"]}
        assert names == {"Item 1", "Item 2"}  # Check names exist without caring about order

    def test_update_endpoint_success(self, test_client, auth_headers):
        create_response = test_client.post(
            "/api/v1/repository/test-items", json={"data": {"name": "Original Item"}}, headers=auth_headers
        )
        created_id = create_response.json()["data"]["data"]["id"]

        response = test_client.put(
            f"/api/v1/repository/test-items",
            json={"id": created_id, "data": {"name": "Updated Item"}},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["data"]["name"] == "Updated Item"
        assert "updated_at" in data["data"]

    def test_delete_endpoint_success(self, test_client, auth_headers):
        create_response = test_client.post(
            "/api/v1/repository/test-items", json={"data": {"name": "To Delete"}}, headers=auth_headers
        )
        created_id = create_response.json()["data"]["data"]["id"]

        response = test_client.delete(f"/api/v1/repository/test-items/{created_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == created_id
        assert "deleted_at" in data["data"]

    def test_unauthorized_access(self, test_client):
        response = test_client.get(
            "/api/v1/repository/test-items",
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    def test_forbidden_access(self, test_client):
        response = test_client.get("/api/v1/repository/test-items", headers={"X-Auth-Token": "wrong_token"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"
