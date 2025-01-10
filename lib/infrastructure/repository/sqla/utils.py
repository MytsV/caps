import functools
import os
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar
from sqlalchemy.orm import Session
from yaml import load, Loader

from lib.infrastructure.repository.sqla.database import Database


Param = ParamSpec("Param")
RetType = TypeVar("RetType")


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

    if yaml_config_file:
        config_file = yaml_config_file
    else:
        # take the `config.yaml` from the root path
        config_file = "config.yaml"

        if not os.path.exists(config_file):
            raise FileNotFoundError(
                f"Config file not provided, and '{config_file}' not found in the root path '{os.getcwd()}'."
            )

    with open(config_file, "r") as file:
        config = load(file, Loader=Loader)

    try:
        db_host = f"{config["rdbms"]["host"]}"
        db_port = config["rdbms"]["port"]
        db_name = config["rdbms"]["database"]
        db_user = config["rdbms"]["username"]
        db_password = config["rdbms"]["password"]
    except:
        raise KeyError(
            f"Config file '{config_file}' does not have the required keys for the RDBMS connection. Please check that the rdbms section contains host, port, database, username and password."
        )

    # TODO: if value is found, it may contain an environment variable in this shape ${ENV_VAR:default}, we need to parse it

    def decorator(func: Callable[Concatenate[Any, Session, Param], RetType]) -> Callable[..., RetType]:
        @functools.wraps(func)
        def wrapper(self: Any, *args: Any, **kwargs: Any) -> RetType:
            session = Database(
                db_host=db_host,
                db_port=db_port,
                db_user=db_user,
                db_password=db_password,
                db_name=db_name,
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
