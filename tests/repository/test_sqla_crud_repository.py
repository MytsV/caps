from datetime import datetime
from unittest.mock import patch

from lib.core.dto import SuccessDTO
from lib.core.error import BaseError
from lib.core.models import BaseSDKModel, EntitySDKModel
from lib.core.secondary_ports import (
    CreatedDTO,
    CreateRequest,
    GetRequest,
    DeleteRequest,
    DeletedDTO,
    UpdateRequest,
    UpdatedDTO,
    BaseCrudRequest,
)
from lib.infrastructure.repository.sqla.database import Base
from lib.infrastructure.repository.sqla.models import SoftModelBase
from sqlalchemy import Column, Integer, String
import pytest

from lib.infrastructure.repository.sqla.sqla_crud_repository import BaseSqlaCrudRepository


class TestSDKModel(EntitySDKModel):
    id: int | None = None
    name: str


class TestPartialSDKModel(BaseSDKModel):
    name: str
    extra_field: str | None = None


class TestSQLModel(Base, SoftModelBase):
    __tablename__ = "test_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_sdk_model(self) -> TestSDKModel:
        return TestSDKModel(id=self.id, name=self.name)


class TestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository):
        yield
        session = repository.session()
        session.query(TestSQLModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return BaseSqlaCrudRepository(TestSQLModel)


class TestCreateBaseSqlaCrudRepository(TestSetup):
    def test_create_success(self, repository):
        create_request = CreateRequest(data=TestPartialSDKModel(name="Test Item"))

        result = repository.create(create_request)

        assert isinstance(result, CreatedDTO)
        assert result.data.data.name == "Test Item"
        assert result.data.data.id is not None
        assert isinstance(result.data.created_at, datetime)

    def test_create_error_handling(self, repository):
        create_request = CreateRequest(data=TestPartialSDKModel(name="Test Item"))

        with patch.object(TestSQLModel, "save", side_effect=Exception("Database error")):
            result = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert result.errorType == "ErrorCreatingNewEntity"
        assert "Database error" in result.message

    def test_create_with_extra_fields(self, repository):
        create_request = CreateRequest(data=TestPartialSDKModel(name="Test Item", extra_field="Should be ignored"))

        result = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert "Invalid field" in result.message


class TestGetBaseSqlaCrudRepository(TestSetup):
    def test_get_existing(self, repository):
        create_request = CreateRequest(data=TestSDKModel(name="Test Item"))
        created = repository.create(create_request)

        get_request = GetRequest(id=created.data.data.id)

        result = repository.get(get_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Test Item"

    def test_get_non_existing(self, repository):
        get_request = GetRequest(id=999)

        result = repository.get(get_request)

        assert isinstance(result, BaseError)
        assert "not found" in result.message


class TestListBaseSqlaCrudRepository(TestSetup):
    def test_list_empty(self, repository):
        result = repository.list(BaseCrudRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 0

    def test_list_multiple_items(self, repository):
        repository.create(CreateRequest(data=TestPartialSDKModel(name="Item 1")))
        repository.create(CreateRequest(data=TestPartialSDKModel(name="Item 2")))

        result = repository.list(BaseCrudRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 2
        assert {item.name for item in result.data} == {"Item 1", "Item 2"}


class TestUpdateBaseSqlaCrudRepository(TestSetup):
    def test_update_existing(self, repository):
        created = repository.create(CreateRequest(data=TestPartialSDKModel(name="Original")))

        update_request = UpdateRequest(id=created.data.data.id, data=TestPartialSDKModel(name="Updated"))

        result = repository.update(update_request)

        assert isinstance(result, UpdatedDTO)
        assert result.data.data.name == "Updated"
        assert isinstance(result.data.updated_at, datetime)

    def test_update_nonexistent(self, repository):
        update_request = UpdateRequest(id=999, data=TestPartialSDKModel(name="Updated"))

        result = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert "not found" in result.message

    def test_update_with_invalid_fields(self, repository):
        created = repository.create(CreateRequest(data=TestPartialSDKModel(name="Original")))

        update_request = UpdateRequest(
            id=created.data.data.id, data=TestPartialSDKModel(name="Updated", extra_field="value")
        )

        result = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert "Invalid field" in result.message


class TestDeleteBaseSqlaCrudRepository(TestSetup):
    def test_delete_existing(self, repository):
        created = repository.create(CreateRequest(data=TestPartialSDKModel(name="To Delete")))

        delete_request = DeleteRequest(id=created.data.data.id)

        result = repository.delete(delete_request)

        assert isinstance(result, DeletedDTO)
        assert result.data.id == created.data.data.id
        assert isinstance(result.data.deleted_at, datetime)

        get_result = repository.get(GetRequest(id=created.data.data.id))
        assert isinstance(get_result, BaseError)
        assert "not found" in get_result.message

    def test_delete_nonexistent(self, repository):
        delete_request = DeleteRequest(id=999)

        result = repository.delete(delete_request)

        assert isinstance(result, BaseError)
        assert "not found" in result.message

    def test_delete_already_deleted(self, repository):
        created = repository.create(CreateRequest(data=TestPartialSDKModel(name="To Delete")))
        first_delete = repository.delete(DeleteRequest(id=created.data.data.id))

        second_delete = repository.delete(DeleteRequest(id=created.data.data.id))

        assert isinstance(second_delete, BaseError)
        assert "not found" in second_delete.message
