import os
import tempfile
from yaml import dump

import pytest

from lib.sdk.infrastructure.repository.sqla.utils import get_database_config


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
                "engine": "postgresql",
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

        assert result.db_engine == "postgresql"
        assert result.db_host == "localhost"
        assert result.db_port == 5433
        assert result.db_name == "test_db"
        assert result.db_user == "test_user"
        assert result.db_password == "test_password"

    def test_env_config(self, temp_config_file):
        os.environ.update(
            {
                "RDBMS_ENGINE": "postgresql",
                "RDBMS_HOST": "env-host",
                "RDBMS_PORT": "5434",
                "RDBMS_DB": "env_db",
                "RDBMS_USER": "env_user",
                "RDBMS_PASSWORD": "env_pass",
            }
        )

        config = {
            "rdbms": {
                "engine": "${RDBMS_ENGINE}",
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

        assert result.db_engine == "postgresql"
        assert result.db_host == "env-host"
        assert result.db_port == 5434
        assert result.db_name == "env_db"
        assert result.db_user == "env_user"
        assert result.db_password == "env_pass"

    def test_mixed_config(self, temp_config_file):
        os.environ["RDBMS_PASSWORD"] = "env_pass"

        config = {
            "rdbms": {
                "engine": "postgresql",
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

        assert result.db_engine == "postgresql"
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
