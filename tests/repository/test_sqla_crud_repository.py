import os
from datetime import datetime
from unittest.mock import patch

from lib.core.dto import SuccessDTO
from lib.core.error import BaseError
from lib.infrastructure.secondary_ports import (
    CreatedDTO,
    CreateRequest,
    GetRequest,
    DeleteRequest,
    DeletedDTO,
    UpdateRequest,
    UpdatedDTO,
    BaseCrudRequest,
)
import pytest

from lib.infrastructure.repository.sqla.utils import get_database_config

from yaml import dump
import tempfile

from tests.repository.models import TestSqlaModel, TestPartialCoreModel, TestCoreModel, TestSetup


class TestCreateBaseSqlaCrudRepository(TestSetup):
    def test_create_success(self, repository):
        create_request = CreateRequest(data=TestPartialCoreModel(name="Test Item").model_dump())

        result = repository.create(create_request)

        assert isinstance(result, CreatedDTO)
        assert result.data.data.name == "Test Item"
        assert result.data.data.id is not None
        assert isinstance(result.data.created_at, datetime)

    def test_create_error_handling(self, repository):
        create_request = CreateRequest(data=TestPartialCoreModel(name="Test Item").model_dump())

        with patch.object(TestSqlaModel, "save", side_effect=Exception("Database error")):
            result = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert result.errorType == "database_error"
        assert "Database error" in result.message

    def test_create_with_extra_fields(self, repository):
        create_request = CreateRequest(
            data=TestPartialCoreModel(name="Test Item", extra_field="Should be ignored").model_dump()
        )

        result = repository.create(create_request)

        assert isinstance(result, BaseError)
        assert "Invalid field" in result.message


class TestGetBaseSqlaCrudRepository(TestSetup):
    def test_get_existing(self, repository):
        create_request = CreateRequest(data=TestCoreModel(name="Test Item").model_dump())
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
        repository.create(CreateRequest(data=TestPartialCoreModel(name="Item 1").model_dump()))
        repository.create(CreateRequest(data=TestPartialCoreModel(name="Item 2").model_dump()))

        result = repository.list(BaseCrudRequest())

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 2
        assert {item.name for item in result.data} == {"Item 1", "Item 2"}


class TestUpdateBaseSqlaCrudRepository(TestSetup):
    def test_update_existing(self, repository):
        created = repository.create(CreateRequest(data=TestPartialCoreModel(name="Original").model_dump()))

        update_request = UpdateRequest(id=created.data.data.id, data=TestPartialCoreModel(name="Updated").model_dump())

        result = repository.update(update_request)

        assert isinstance(result, UpdatedDTO)
        assert result.data.data.name == "Updated"
        assert isinstance(result.data.updated_at, datetime)

    def test_update_nonexistent(self, repository):
        update_request = UpdateRequest(id=999, data=TestPartialCoreModel(name="Updated").model_dump())

        result = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert "not found" in result.message

    def test_update_with_invalid_fields(self, repository):
        created = repository.create(CreateRequest(data=TestPartialCoreModel(name="Original").model_dump()))

        update_request = UpdateRequest(
            id=created.data.data.id, data=TestPartialCoreModel(name="Updated", extra_field="value").model_dump()
        )

        result = repository.update(update_request)

        assert isinstance(result, BaseError)
        assert "Invalid field" in result.message


class TestDeleteBaseSqlaCrudRepository(TestSetup):
    def test_delete_existing(self, repository):
        created = repository.create(CreateRequest(data=TestPartialCoreModel(name="To Delete").model_dump()))

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
        created = repository.create(CreateRequest(data=TestPartialCoreModel(name="To Delete").model_dump()))
        first_delete = repository.delete(DeleteRequest(id=created.data.data.id))

        second_delete = repository.delete(DeleteRequest(id=created.data.data.id))

        assert isinstance(second_delete, BaseError)
        assert "not found" in second_delete.message


class TestGetDatabaseConfig:
    @pytest.fixture
    def temp_config_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yield f.name
        # Cleanup after test
        os.unlink(f.name)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.original_env = {
            key: os.getenv(key)
            for key in ["CONFIG_PATH", "RDBMS_HOST", "RDBMS_PORT", "RDBMS_DB", "RDBMS_USER", "RDBMS_PASSWORD"]
        }
        yield
        for key, value in self.original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_constant_config(self, temp_config_file):
        config = {
            "rdbms": {
                "host": "localhost",
                "port": "5433",
                "database": "test_db",
                "username": "test_user",
                "password": "test_password",
            }
        }
        with open(temp_config_file, "w") as f:
            dump(config, f)

        result = get_database_config(temp_config_file)

        assert result.db_host == "localhost"
        assert result.db_port == 5433
        assert result.db_name == "test_db"
        assert result.db_user == "test_user"
        assert result.db_password == "test_password"

    def test_env_config(self, temp_config_file):
        os.environ.update(
            {
                "RDBMS_HOST": "env-host",
                "RDBMS_PORT": "5434",
                "RDBMS_DB": "env_db",
                "RDBMS_USER": "env_user",
                "RDBMS_PASSWORD": "env_pass",
            }
        )

        config = {
            "rdbms": {
                "host": "${RDBMS_HOST}",
                "port": "${RDBMS_PORT}",
                "database": "${RDBMS_DB}",
                "username": "${RDBMS_USER}",
                "password": "${RDBMS_PASSWORD}",
            }
        }
        with open(temp_config_file, "w") as f:
            dump(config, f)

        result = get_database_config(temp_config_file)

        assert result.db_host == "env-host"
        assert result.db_port == 5434
        assert result.db_name == "env_db"
        assert result.db_user == "env_user"
        assert result.db_password == "env_pass"

    def test_mixed_config(self, temp_config_file):
        os.environ["RDBMS_PASSWORD"] = "env_pass"

        config = {
            "rdbms": {
                "host": "${RDBMS_HOST:localhost}",
                "port": "${RDBMS_PORT:5433}",
                "database": "test_db",
                "username": "${RDBMS_USER:test_user}",
                "password": "${RDBMS_PASSWORD}",
            }
        }
        with open(temp_config_file, "w") as f:
            dump(config, f)

        result = get_database_config(temp_config_file)

        assert result.db_host == "localhost"
        assert result.db_port == 5433
        assert result.db_name == "test_db"
        assert result.db_user == "test_user"
        assert result.db_password == "env_pass"

    def test_missing_required_key(self, temp_config_file):
        config = {"rdbms": {"host": "localhost", "database": "test_db"}}
        with open(temp_config_file, "w") as f:
            dump(config, f)

        with pytest.raises(KeyError) as exc_info:
            get_database_config(temp_config_file)
        assert "required" in str(exc_info.value)
