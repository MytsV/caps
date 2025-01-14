from datetime import datetime
from typing import List

from lib.core.models import BaseCoreModel
from lib.infrastructure.secondary_ports import (
    CreateRequest,
    UpdateRequest,
    DeleteRequest,
    CreatedDTO,
    UpdatedDTO,
    DeletedDTO,
    BaseCrudRepositoryOutputPort,
    UpdatedData,
    CreatedData,
    DeletedData,
)
from lib.core.dto import SuccessDTO


# Mock implementations
class MockEntity(BaseCoreModel):
    id: int
    name: str


class MockCreateRequest(CreateRequest):
    data: MockEntity


class MockUpdateRequest(UpdateRequest):
    id: int
    data: MockEntity


class MockDeleteRequest(DeleteRequest):
    id: int


class MockRepository(BaseCrudRepositoryOutputPort):
    def create(self, session: str, request: MockCreateRequest) -> CreatedDTO[MockEntity]:
        return CreatedDTO[MockEntity](data=CreatedData[MockEntity](data=request.data, created_at=datetime.now()))

    def get(self, session: str, request: CreateRequest) -> SuccessDTO[MockEntity]:
        return SuccessDTO(data={"id": 1, "name": "Test Entity"})

    def list(self, session: str, request: CreateRequest) -> SuccessDTO[List[MockEntity]]:
        return SuccessDTO(data=[{"id": 1, "name": "Test Entity"}])

    def update(self, session: str, request: MockUpdateRequest) -> UpdatedDTO[MockEntity]:
        return UpdatedDTO[MockEntity](data=UpdatedData[MockEntity](data=request.data, updated_at=datetime.now()))

    def delete(self, session: str, request: MockDeleteRequest) -> DeletedDTO[MockEntity]:
        return DeletedDTO[MockEntity](data=DeletedData[MockEntity](id=request.id, deleted_at=datetime.now()))


# Tests
def test_create_method():
    repo = MockRepository()
    mock_request = MockCreateRequest(data=MockEntity(id=1, name="Test Entity"))
    response = repo.create(session="mock_session", request=mock_request)

    assert response.data.data.id == 1
    assert response.data.data.name == "Test Entity"
    assert isinstance(response.data.created_at, datetime)


def test_get_method():
    repo = MockRepository()
    mock_request = MockCreateRequest(data=MockEntity(id=1, name="Test Entity"))
    response = repo.get(session="mock_session", request=mock_request)

    assert response.data["id"] == 1
    assert response.data["name"] == "Test Entity"


def test_list_method():
    repo = MockRepository()
    mock_request = MockCreateRequest(data=MockEntity(id=1, name="Test Entity"))
    response = repo.list(session="mock_session", request=mock_request)

    assert len(response.data) == 1
    assert response.data[0]["id"] == 1
    assert response.data[0]["name"] == "Test Entity"


def test_update_method():
    repo = MockRepository()
    mock_request = MockUpdateRequest(id=1, data=MockEntity(id=1, name="Updated Entity"))
    response = repo.update(session="mock_session", request=mock_request)

    assert response.data.data.id == 1
    assert response.data.data.name == "Updated Entity"
    assert isinstance(response.data.updated_at, datetime)


def test_delete_method():
    repo = MockRepository()
    mock_request = MockDeleteRequest(id=1)
    response = repo.delete(session="mock_session", request=mock_request)

    assert response.data.id == 1
    assert isinstance(response.data.deleted_at, datetime)
