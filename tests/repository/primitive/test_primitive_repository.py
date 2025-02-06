from unittest.mock import patch

from pydantic import BaseModel

from lib.sdk.core.dto import SuccessDTO
from lib.sdk.core.error import BaseError
import pytest

from lib.sdk.core.request import BaseIdentifiedRequest
from tests.repository.primitive.primitive_secondary_entities import (
    PrimitiveTestSetup,
    PrimitiveCreateRequest,
    PrimitiveGetRequest,
    PrimitiveListRequest,
    PrimitiveUpdateRequest,
    PrimitiveDeleteRequest,
    PrimitiveRepository,
    PrimitiveCreateDTO,
    PrimitiveGetDTO,
    PrimitiveListDTO,
    PrimitiveUpdateDTO,
    PrimitiveDeleteDTO,
)
from tests.repository.sqla_models import PrimitiveSqlaModel


class PrimitiveCreateExtraFieldsRequest(BaseModel):
    name: str
    extra_field: str


class PrimitiveUpdateExtraFieldsRequest(BaseIdentifiedRequest):
    name: str
    extra_field: str


class TestCreatePrimitiveRepository(PrimitiveTestSetup):
    def test_create_success(self, repository: PrimitiveRepository) -> None:
        create_request: PrimitiveCreateRequest = PrimitiveCreateRequest(name="Test Item")

        result: PrimitiveCreateDTO = repository.create(create_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Test Item"
        assert result.data.id is not None

    def test_create_error_handling(self, repository: PrimitiveRepository) -> None:
        create_request: PrimitiveCreateRequest = PrimitiveCreateRequest(name="Test Item")

        with patch.object(PrimitiveSqlaModel, "save", side_effect=Exception("Database error")):
            result: PrimitiveCreateDTO = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert result.error_type == "database"


class TestGetPrimitiveRepository(PrimitiveTestSetup):
    def test_get_existing(self, repository: PrimitiveRepository) -> None:
        create_request: PrimitiveCreateRequest = PrimitiveCreateRequest(name="Test Item")
        created: PrimitiveCreateDTO = repository.create(create_request)

        if isinstance(created, BaseError):
            raise Exception(created.message)

        get_request: PrimitiveGetRequest = PrimitiveGetRequest(id=created.data.id)

        result: PrimitiveGetDTO = repository.get(get_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Test Item"

    def test_get_non_existing(self, repository: PrimitiveRepository) -> None:
        get_request: PrimitiveGetRequest = PrimitiveGetRequest(id=999)

        result: PrimitiveGetDTO = repository.get(get_request)

        assert isinstance(result, BaseError)
        assert result.error_type == "not_found"


class TestListPrimitiveRepository(PrimitiveTestSetup):
    def test_list_empty(self, repository: PrimitiveRepository) -> None:
        result: PrimitiveListDTO = repository.list(PrimitiveListRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 0

    def test_list_multiple_items(self, repository: PrimitiveRepository) -> None:
        repository.create(PrimitiveCreateRequest(name="Item 1"))
        repository.create(PrimitiveCreateRequest(name="Item 2"))

        result: PrimitiveListDTO = repository.list(PrimitiveListRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 2
        assert {item.name for item in result.data} == {"Item 1", "Item 2"}


class TestUpdatePrimitiveRepository(PrimitiveTestSetup):
    def test_update_existing(self, repository: PrimitiveRepository) -> None:
        created: PrimitiveCreateDTO = repository.create(PrimitiveCreateRequest(name="Original"))

        if isinstance(created, BaseError):
            raise Exception(created.message)

        update_request: PrimitiveUpdateRequest = PrimitiveUpdateRequest(id=created.data.id, name="Updated")

        result: PrimitiveUpdateDTO = repository.update(update_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Updated"

    def test_update_nonexistent(self, repository: PrimitiveRepository) -> None:
        update_request: PrimitiveUpdateRequest = PrimitiveUpdateRequest(id=999, name="Updated")

        result: PrimitiveUpdateDTO = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert result.error_type == "not_found"


class TestDeletePrimitiveRepository(PrimitiveTestSetup):
    def test_delete_existing(self, repository: PrimitiveRepository) -> None:
        created: PrimitiveCreateDTO = repository.create(PrimitiveCreateRequest(name="To Delete"))

        if isinstance(created, BaseError):
            raise Exception(created.message)

        delete_request: PrimitiveDeleteRequest = PrimitiveDeleteRequest(id=created.data.id)

        result: PrimitiveDeleteDTO = repository.delete(delete_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.id == created.data.id

        get_result: PrimitiveGetDTO = repository.get(PrimitiveGetRequest(id=created.data.id))
        assert isinstance(get_result, BaseError)
        assert get_result.error_type == "not_found"

    def test_delete_nonexistent(self, repository: PrimitiveRepository) -> None:
        delete_request: PrimitiveDeleteRequest = PrimitiveDeleteRequest(id=999)

        result: PrimitiveDeleteDTO = repository.delete(delete_request)

        assert isinstance(result, BaseError)
        assert result.error_type == "not_found"

    def test_delete_already_deleted(self, repository: PrimitiveRepository) -> None:
        created: PrimitiveCreateDTO = repository.create(PrimitiveCreateRequest(name="To Delete"))

        if isinstance(created, BaseError):
            raise Exception(created.message)

        first_delete: PrimitiveDeleteDTO = repository.delete(PrimitiveDeleteRequest(id=created.data.id))

        second_delete: PrimitiveDeleteDTO = repository.delete(PrimitiveDeleteRequest(id=created.data.id))

        assert isinstance(second_delete, BaseError)
        assert second_delete.error_type == "not_found"
