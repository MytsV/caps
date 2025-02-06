from typing import Dict, Any, Optional

from lib.sdk.infrastructure.fastapi.endpoint_descriptor import BaseEndpointDescriptor
from lib.sdk.infrastructure.fastapi.fastapi_endpoint import (
    BaseFastAPIEndpoint,
    default_error_handler,
    mock_authenticate,
)
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.repository.primitive.primitive_secondary_entities import (
    PrimitiveTestSetup,
    PrimitiveCreateDTO,
    PrimitiveCreateRequest,
    PrimitiveGetDTO,
    PrimitiveGetRequest,
    PrimitiveListDTO,
    PrimitiveListRequest,
    PrimitiveUpdateDTO,
    PrimitiveUpdateRequest,
    PrimitiveDeleteDTO,
    PrimitiveDeleteRequest,
    PrimitiveRepository,
)


class PrimitiveEndpoint(BaseFastAPIEndpoint):
    def __init__(
        self,
        descriptor: BaseEndpointDescriptor,
        responses: Dict[int | str, dict[str, Any]],
        repository: PrimitiveRepository,
    ) -> None:
        super().__init__(descriptor, responses)
        self.prefix += "/repository"
        self._repository = repository

    def authenticate(self, x_auth_token: str) -> None:
        mock_authenticate(x_auth_token)

    def register_endpoint(self) -> None:
        @self.router.post(
            f"{self.prefix}/{self._name}",
            response_model=PrimitiveCreateDTO,
            responses=self.responses,
        )
        @default_error_handler()
        async def create(request: PrimitiveCreateRequest) -> PrimitiveCreateDTO:
            result = self._repository.create(request=request)
            return result

        @self.router.get(
            f"{self.prefix}/{self._name}/{{id}}",
            response_model=PrimitiveGetDTO,
            responses=self.responses,
        )
        @default_error_handler()
        async def get(id: int) -> PrimitiveGetDTO:
            result = self._repository.get(request=PrimitiveGetRequest(id=id))
            return result

        @self.router.get(
            f"{self.prefix}/{self._name}",
            response_model=PrimitiveListDTO,
            responses=self.responses,
        )
        @default_error_handler()
        async def list(
            page: Optional[int] = None,
            page_size: Optional[int] = None,
        ) -> PrimitiveListDTO:
            result = self._repository.list(
                request=PrimitiveListRequest(
                    page=page,
                    page_size=page_size,
                ),
            )
            return result

        @self.router.put(
            f"{self.prefix}/{self._name}",
            response_model=PrimitiveUpdateDTO,
            responses=self.responses,
        )
        @default_error_handler()
        async def update(request: PrimitiveUpdateRequest) -> PrimitiveUpdateDTO:
            result = self._repository.update(request=request)
            return result

        @self.router.delete(
            f"{self.prefix}/{self._name}/{{id}}",
            response_model=PrimitiveDeleteDTO,
            responses=self.responses,
        )
        @default_error_handler()
        async def delete(id: int) -> PrimitiveDeleteDTO:
            result = self._repository.delete(
                request=PrimitiveDeleteRequest(id=id),
            )
            return result


class TestPrimitiveBypassEndpoint(PrimitiveTestSetup):
    @pytest.fixture
    def app(self) -> FastAPI:
        return FastAPI()

    @pytest.fixture
    def test_client(self, app: FastAPI, endpoint: PrimitiveEndpoint) -> TestClient:
        router = endpoint.load()
        if router is None:
            raise ValueError("Failed to load endpoint")
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def descriptor(self) -> BaseEndpointDescriptor:
        return BaseEndpointDescriptor(
            name="test-items",
            description="Test CRUD operations for items",
            version="1.0.0",
            tags=["test", "crud"],
            enabled=True,
            auth=True,
        )

    @pytest.fixture
    def responses(self) -> Dict[int | str, dict[str, Any]]:
        return {
            400: {"description": "Validation Error"},
            401: {"description": "Unauthorized"},
            403: {"description": "Forbidden"},
            404: {"description": "Not Found"},
            500: {"description": "Internal Server Error"},
        }

    @pytest.fixture
    def endpoint(
        self,
        repository: PrimitiveRepository,
        descriptor: BaseEndpointDescriptor,
        responses: Dict[int | str, dict[str, Any]],
    ) -> PrimitiveEndpoint:
        return PrimitiveEndpoint(repository=repository, descriptor=descriptor, responses=responses)

    @pytest.fixture
    def auth_headers(self) -> Dict[str, str]:
        return {"X-Auth-Token": "test123"}

    def test_create_endpoint_success(self, test_client: TestClient, auth_headers: Dict[str, str]) -> None:
        response = test_client.post("/api/v1/repository/test-items", json={"name": "New Item"}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "New Item"
        assert isinstance(data["data"]["id"], int)

    def test_get_endpoint_success(self, test_client: TestClient, auth_headers: Dict[str, str]) -> None:
        create_response = test_client.post(
            "/api/v1/repository/test-items", json={"name": "Test Item"}, headers=auth_headers
        )
        created_id = create_response.json()["data"]["id"]

        response = test_client.get(f"/api/v1/repository/test-items/{created_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Test Item"
        assert data["data"]["id"] == created_id

    def test_get_endpoint_not_found(self, test_client: TestClient, auth_headers: Dict[str, str]) -> None:
        response = test_client.get("/api/v1/repository/test-items/999", headers=auth_headers)
        assert response.status_code == 404
        data = response.json()
        assert data["errorType"] == "not_found"

    def test_list_endpoint_success(self, test_client: TestClient, auth_headers: Dict[str, str]) -> None:
        test_client.post("/api/v1/repository/test-items", json={"name": "Item 1"}, headers=auth_headers)
        test_client.post("/api/v1/repository/test-items", json={"name": "Item 2"}, headers=auth_headers)

        response = test_client.get("/api/v1/repository/test-items", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2
        names = {item["name"] for item in data["data"]}
        assert names == {"Item 1", "Item 2"}

    def test_update_endpoint_success(self, test_client: TestClient, auth_headers: Dict[str, str]) -> None:
        create_response = test_client.post(
            "/api/v1/repository/test-items", json={"name": "Original Item"}, headers=auth_headers
        )
        created_id = create_response.json()["data"]["id"]

        response = test_client.put(
            f"/api/v1/repository/test-items",
            json={"id": created_id, "name": "Updated Item"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Item"

    def test_delete_endpoint_success(self, test_client: TestClient, auth_headers: Dict[str, str]) -> None:
        create_response = test_client.post(
            "/api/v1/repository/test-items", json={"name": "To Delete"}, headers=auth_headers
        )
        created_id = create_response.json()["data"]["id"]

        response = test_client.delete(f"/api/v1/repository/test-items/{created_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == created_id

    def test_unauthorized_access(self, test_client: TestClient) -> None:
        response = test_client.get("/api/v1/repository/test-items", headers={})
        assert response.status_code == 401
        assert response.json()["detail"] == "Unauthorized"

    def test_forbidden_access(self, test_client: TestClient) -> None:
        response = test_client.get("/api/v1/repository/test-items", headers={"X-Auth-Token": "wrong_token"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Forbidden"
