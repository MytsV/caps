import hashlib
import random
import time
from enum import Enum
from functools import wraps
from typing import Callable, Literal, Dict, Any, Union, ParamSpec, TypeVar, Optional

from lib.sdk.core.models import BaseCoreModel, BaseCamelCaseModel


class ErrorType(str, Enum):
    NOT_FOUND = "not_found"
    VALIDATION = "validation"
    DATABASE = "database"
    UNKNOWN = "unknown"


class BaseError(BaseCamelCaseModel):
    """
    An error class for the project, to represent 'soft' errors and expected exceptions.

    @param success: The status of the operation, with False meaning 'error'
    @type success: Literal[False]
    @param name: A human readable title for the error
    @type name: str
    @param digest: A hash that can be used to trace the error in the logs. Users are expected to contact us with the digest id.
    @type digest: str
    @param message: A user readable string indicating the error. This should not include secrets or any other information that is not relevant to the end user. This is important to allow bypassing errors from gateways to presenters.
    @type message: str
    @param context: A generic object that can be logged on the server side. The fields like type, code (not errorCode, errorType as that is implied) can be included in the context.
    """

    success: Literal[False] = False
    name: str
    digest: str
    message: str
    context: object  # TODO: pydantic cannot serialize some objects!
    error_type: ErrorType


class NotFoundError(Exception):
    error_type = ErrorType.NOT_FOUND

    def __init__(self, message: str, context: object = None):
        self.context = {} if context is None else context
        self.message = message


class ValidationError(Exception):
    error_type = ErrorType.VALIDATION

    def __init__(self, message: str, context: object = None):
        self.context = {} if context is None else context
        self.message = message


class DatabaseError(Exception):
    error_type = ErrorType.DATABASE

    def __init__(self, message: str, context: object = None):
        self.context = {} if context is None else context
        self.message = message


def generate_digest() -> str:
    timestamp = str(time.time())
    random_string = str(random.randint(0, 1000000))
    return hashlib.md5(f"{timestamp}{random_string}".encode()).hexdigest()[:8]


P = ParamSpec("P")
R = TypeVar("R")


def exception_handler(digest: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, Union[R, BaseError]]]:
    def decorator(func: Callable[P, R]) -> Callable[P, Union[R, BaseError]]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> Union[R, BaseError]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type: ErrorType = getattr(e, "error_type", ErrorType.UNKNOWN)
                message: str = getattr(e, "message", str(e))
                context: Dict[str, Any] = getattr(e, "context", {})

                return BaseError(
                    name=type(e).__name__,
                    digest=digest or generate_digest(),
                    message=message,
                    context=context,
                    error_type=error_type,
                )

        return wrapper

    return decorator
