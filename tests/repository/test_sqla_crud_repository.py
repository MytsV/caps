from datetime import datetime
from unittest.mock import patch

from lib.core.dto import SuccessDTO
from lib.core.error import BaseError
from lib.core.models import BaseSDKModel, EntitySDKModel
from lib.core.secondary_ports import CreatedDTO, CreateRequest, GetRequest
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

    def test_get_existing(self, repository):
        create_request = CreateRequest(data=TestSDKModel(name="Test Item"))
        created = repository.create(create_request)

        get_request = GetRequest(id=created.data.data.id)

        result = repository.get(get_request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Test Item"
