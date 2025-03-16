import os
from typing import Any, Callable, TypeVar, Optional, cast
from yaml import load, Loader
from pydantic import BaseModel

from lib.sdk.infrastructure.repository.sqla.database import Database


def parse_config_value(value: Any) -> Any:
    """Parse a single config value that could be:
    - constant value
    - env var reference
    - env var with default

    Args:
        value: The configuration value to parse

    Returns:
        The parsed configuration value
    """
    if not isinstance(value, str):
        return value

    if not value.startswith("${"):
        return value

    env_var: str = value[2:-1]  # Remove ${ and }
    if ":" in env_var:
        var_name, default = env_var.split(":", 1)
        return os.getenv(var_name, default)
    else:
        return os.getenv(env_var)


def resolve_config_path(yaml_config_file: Optional[str] = None) -> str:
    """
    Resolve the config file path based on:
    1. Passed argument
    2. Environment variable
    3. Default path

    Args:
        yaml_config_file: Optional path to the YAML config file

    Returns:
        str: The resolved path to the config file

    Raises:
        FileNotFoundError: If no valid config file path is found
    """
    if yaml_config_file:
        return yaml_config_file

    env_config_path: Optional[str] = os.getenv("CONFIG_PATH")
    if env_config_path:
        return env_config_path

    default_path: str = "config.yaml"
    if not os.path.exists(default_path):
        raise FileNotFoundError(
            f"Config file not found. Tried:\n"
            f"- Passed argument: None\n"
            f"- Environment variable CONFIG_PATH: {env_config_path}\n"
            f"- Default path: {default_path} (in {os.getcwd()})"
        )

    return default_path


class DatabaseConfig(BaseModel):
    db_engine: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str


def get_database_config(yaml_config_file: Optional[str] = None) -> DatabaseConfig:
    """
    Get database configuration from YAML file

    Args:
        yaml_config_file: Optional path to the YAML config file

    Returns:
        DatabaseConfig: The parsed database configuration

    Raises:
        KeyError: If required configuration keys are missing
    """
    config_file: str = resolve_config_path(yaml_config_file)

    with open(config_file, "r") as file:
        config: dict[str, Any] = load(file, Loader=Loader)

    try:
        rdbms_config: dict[str, Any] = config["rdbms"]
        return DatabaseConfig(
            db_engine=parse_config_value(rdbms_config["engine"]),
            db_host=parse_config_value(rdbms_config["host"]),
            db_port=int(parse_config_value(rdbms_config["port"])),
            db_name=parse_config_value(rdbms_config["database"]),
            db_user=parse_config_value(rdbms_config["username"]),
            db_password=parse_config_value(rdbms_config["password"]),
        )
    except:
        raise KeyError(
            f"Config file '{config_file}' does not have the required keys for the RDBMS connection. Please check that the rdbms section contains host, port, database, username and password."
        )


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def sqla_database_context(
    yaml_config_file: Optional[str] = None,
) -> Callable[[FuncT], FuncT]:
    """
    A decorator that provides a SQLAlchemy session to the decorated function.
    This must be used in a class method where the class has a `session_generator`.
    The `session_generator` must be a generator that yields a SQLA session context manager.
    The decorated function must have a `session` argument as it's second argument.
    The first argument must be `self`.

    Args:
        yaml_config_file: Optional path to the YAML config file

    Returns:
        A decorator that wraps the function and provides a session

    Example:
    ```python
        @sqla_database_context()
        def my_function(self, session: Session, arg1, arg2):
            # Function implementation that uses the session
    ```
    """

    config: DatabaseConfig = get_database_config(yaml_config_file)

    def decorator(func: FuncT) -> FuncT:
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            database = Database(
                db_engine=config.db_engine,
                db_host=config.db_host,
                db_port=config.db_port,
                db_user=config.db_user,
                db_password=config.db_password,
                db_name=config.db_name,
            )
            output = func(self, *args, **kwargs, database=database)
            return output

        return cast(FuncT, wrapper)

    return decorator
