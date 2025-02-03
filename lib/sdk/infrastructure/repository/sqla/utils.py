import functools
import os
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar
from sqlalchemy.orm import Session
from yaml import load, Loader
from pydantic import BaseModel

from lib.sdk.infrastructure.repository.sqla.database import Database


Param = ParamSpec("Param")
RetType = TypeVar("RetType")


def parse_config_value(value):
    """Parse a single config value that could be:
    - constant value
    - env var reference
    - env var with default
    """
    if not isinstance(value, str):
        return value

    if not value.startswith("${"):
        return value

    env_var = value[2:-1]  # Remove ${ and }
    if ":" in env_var:
        var_name, default = env_var.split(":", 1)
        return os.getenv(var_name, default)
    else:
        return os.getenv(env_var)


def resolve_config_path(yaml_config_file: str | None = None) -> str:
    """
    Resolve the config file path based on:
    1. Passed argument
    2. Environment variable
    3. Default path
    """
    if yaml_config_file:
        return yaml_config_file

    env_config_path = os.getenv("CONFIG_PATH")
    if env_config_path:
        return env_config_path

    default_path = "config.yaml"
    if not os.path.exists(default_path):
        raise FileNotFoundError(
            f"Config file not found. Tried:\n"
            f"- Passed argument: None\n"
            f"- Environment variable THIS_PROJECT_CONFIG_PATH: {env_config_path}\n"
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


def get_database_config(yaml_config_file: str | None = None) -> DatabaseConfig:
    config_file = resolve_config_path(yaml_config_file)

    with open(config_file, "r") as file:
        config = load(file, Loader=Loader)

    try:
        rdbms_config = config["rdbms"]
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


def sqla_session_context(
    yaml_config_file: str | None = None,
) -> Callable[[Callable[Concatenate[Any, Session, Param], RetType]], Callable[..., RetType]]:
    """
    A decorator that provides a SQLAlchemy session to the decorated function.
    This must be used in a class method where the class has a `session_generator`.
    The `session_generator` must be a generator that yields a SQLA session context manager.
    The decorated function must have a `session` argument as it's second argument.
    The first argument must be `self`.
    This decorator wraps a function and ensures that a SQLAlchemy session is
    created and passed to the function as a keyword argument. The session is
    automatically closed after the function execution.
    Returns:
        Callable[[Callable[Concatenate[Any, Session, Param], RetType]], Callable[..., RetType]]:
        A decorator that wraps the function and provides a session.
    Example:
    ```python
        @sexy_decorator_pipipi()
        def my_function(self, session: Session, arg1, arg2):
            # Function implementation that uses the session
    ```
    """

    config = get_database_config(yaml_config_file)

    # TODO: if value is found, it may contain an environment variable in this shape ${ENV_VAR:default}, we need to parse it

    def decorator(func: Callable[Concatenate[Any, Session, Param], RetType]) -> Callable[..., RetType]:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> RetType:
            session = Database(
                db_engine=config.db_engine,
                db_host=config.db_host,
                db_port=config.db_port,
                db_user=config.db_user,
                db_password=config.db_password,
                db_name=config.db_name,
            ).session_factory()
            try:
                output = func(self, session, *args, **kwargs)
                return output
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()

        return wrapper

    return decorator
