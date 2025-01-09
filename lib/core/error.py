from typing import Callable, Concatenate, Literal

from lib.core.models import BaseSDKModel

import traceback
import uuid


class BaseError(BaseSDKModel):
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
    errorType: Literal["gateway_endpoint_error"] | Literal["database_error"] | str


type TExcFields = Literal[False] | int | str | BaseException


class BaseSDKException(BaseSDKModel):
    """
    An exception class for the project, to represent 'hard' errors and unexpected exceptions.

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
    exception_source: str
    name: str
    digest: str
    message: str
    context: object  # TODO: pydantic cannot serialize some objects!
    errorType: str


type TError = BaseError | BaseSDKException


def serialize_exception(e: Exception) -> dict[str, TExcFields]:
    """Convert an exception object into a JSON-serializable dictionary."""
    return {
        "type": e.__class__.__name__,
        "message": str(e),
        "args": str(e.args),
        "traceback": f"{traceback.format_exc()}",
    }


type TMethod[O, **P, T] = Callable[Concatenate[O, P], T]
type TWrappedMethod[O, **P, T] = Callable[Concatenate[O, P], T | BaseSDKException]


def exception_handler[O, **P, T](digest: str | None) -> Callable[[TMethod[O, P, T]], TWrappedMethod[O, P, T]]:
    """
    A decorator to handle exceptions in methods of a class in a standard way.
    """

    def decorator(method: TMethod[O, P, T]) -> TWrappedMethod[O, P, T]:
        def wrapper(self: O, /, *args: P.args, **kwargs: P.kwargs) -> T | BaseSDKException:
            try:
                return method(self, *args, **kwargs)

            except Exception as e:

                return BaseSDKException(
                    name="Unexpected Exception",
                    exception_source=self.__class__.__name__,
                    digest=digest or str(uuid.uuid4()),
                    message=f"{e}",
                    context={"exception_args": e.args, "traceback": f"{traceback.format_exc()}"},
                    errorType=f"{e.__class__.__name__}",
                )

        return wrapper

    return decorator
