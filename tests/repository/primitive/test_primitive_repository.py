from unittest.mock import patch

from pydantic import BaseModel

from lib.core.dto import SuccessDTO
from lib.core.error import BaseError
import pytest

from lib.core.request import BaseIdentifiedRequest
from tests.repository.primitive.primitive_secondary_entities import (
    PrimitiveTestSetup,
    PrimitiveCreateRequest,
    PrimitiveGetRequest,
    PrimitiveListRequest,
    PrimitiveUpdateRequest,
    PrimitiveDeleteRequest,
)
from tests.repository.sqla_models import PrimitiveSqlaModel


class PrimitiveCreateExtraFieldsRequest(BaseModel):
    name: str
    extra_field: str


class PrimitiveUpdateExtraFieldsRequest(BaseIdentifiedRequest):
    name: str
    extra_field: str


class PrimitiveTestCreatePrimitiveRepository(PrimitiveTestSetup):
    def test_create_success(self, repository):
        create_request = PrimitiveCreateRequest(name="Test Item")

        result = repository.create(create_request)
        print(result)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Test Item"
        assert result.data.id is not None

    def test_create_error_handling(self, repository):
        create_request = PrimitiveCreateRequest(name="Test Item")

        with patch.object(PrimitiveSqlaModel, "save", side_effect=Exception("Database error")):
            result = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert result.error_type == "database_error"
        assert "Database error" in result.message

    def test_create_with_extra_fields(self, repository):
        create_request = PrimitiveCreateExtraFieldsRequest(name="Test Item", extra_field="value")

        result = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert result.error_type == "validation_error"


class PrimitiveTestGetPrimitiveRepository(PrimitiveTestSetup):
    def test_get_existing(self, repository):
        create_request = PrimitiveCreateRequest(name="Test Item")
        created = repository.create(create_request)

        get_request = PrimitiveGetRequest(id=created.data.id)

        result = repository.get(get_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Test Item"

    def test_get_non_existing(self, repository):
        get_request = PrimitiveGetRequest(id=999)

        result = repository.get(get_request)

        assert isinstance(result, BaseError)
        assert "not_found_error" in result.error_type


class PrimitiveTestListPrimitiveRepository(PrimitiveTestSetup):
    def test_list_empty(self, repository):
        result = repository.list(PrimitiveListRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 0

    def test_list_multiple_items(self, repository):
        repository.create(PrimitiveCreateRequest(name="Item 1"))
        repository.create(PrimitiveCreateRequest(name="Item 2"))

        result = repository.list(PrimitiveListRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 2
        assert {item.name for item in result.data} == {"Item 1", "Item 2"}


class PrimitiveTestUpdatePrimitiveRepository(PrimitiveTestSetup):
    def test_update_existing(self, repository):
        created = repository.create(PrimitiveCreateRequest(name="Original"))

        update_request = PrimitiveUpdateRequest(id=created.data.id, name="Updated")

        result = repository.update(update_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Updated"

    def test_update_nonexistent(self, repository):
        update_request = PrimitiveUpdateRequest(id=999, name="Updated")

        result = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert "not_found_error" in result.error_type

    def test_update_with_invalid_fields(self, repository):
        created = repository.create(PrimitiveCreateRequest(name="Original"))

        update_request = PrimitiveUpdateExtraFieldsRequest(id=created.data.id, name="Updated", extra_field="value")

        result = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert "validation_error" in result.error_type


class PrimitiveTestDeletePrimitiveRepository(PrimitiveTestSetup):
    def test_delete_existing(self, repository):
        created = repository.create(PrimitiveCreateRequest(name="To Delete"))

        delete_request = PrimitiveDeleteRequest(id=created.data.id)

        result = repository.delete(delete_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.id == created.data.id

        get_result = repository.get(PrimitiveGetRequest(id=created.data.id))
        assert isinstance(get_result, BaseError)
        assert "not_found_error" in get_result.error_type

    def test_delete_nonexistent(self, repository):
        delete_request = PrimitiveDeleteRequest(id=999)

        result = repository.delete(delete_request)

        assert isinstance(result, BaseError)
        assert "not_found_error" in result.error_type

    def test_delete_already_deleted(self, repository):
        created = repository.create(PrimitiveCreateRequest(name="To Delete"))
        first_delete = repository.delete(PrimitiveDeleteRequest(id=created.data.id))

        second_delete = repository.delete(PrimitiveDeleteRequest(id=created.data.id))

        assert isinstance(second_delete, BaseError)
        assert "not_found_error" in second_delete.error_type
