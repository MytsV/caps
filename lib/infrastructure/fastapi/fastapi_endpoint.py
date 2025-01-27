from abc import ABC, abstractmethod
from enum import Enum
from typing import Annotated, Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status, Body, HTTPException, Response
import logging
from functools import wraps
from typing import Callable
from fastapi.responses import JSONResponse

from lib.core.error import BaseError
from lib.infrastructure.fastapi.endpoint_descriptor import BaseEndpointDescriptor

logger = logging.getLogger(__name__)


class BaseFastAPIEndpoint(ABC):
    def __init__(
        self,
        descriptor: BaseEndpointDescriptor,
        responses: Dict[int | str, dict[str, Any]],
    ) -> None:
        name = descriptor.name
        self._name = name
        self._descriptor = descriptor
        self._responses: Dict[int | str, dict[str, Any]] = responses

        tags: list[str | Enum] = [name]
        tags.extend(descriptor.tags)
        if self._descriptor.auth:
            tags.append("protected")
        else:
            tags.append("public")

        router: APIRouter = APIRouter(
            tags=tags,
        )
        if self._descriptor.auth:
            router.dependencies.append(Depends(self.check_auth))

        self._router = router

        self.prefix = "/api/v1"

    @property
    def name(self) -> str:
        return self._name

    @property
    def descriptor(self) -> BaseEndpointDescriptor:
        return self._descriptor

    @property
    def responses(self) -> Dict[int | str, dict[str, Any]]:
        return self._responses

    @property
    def router(self) -> APIRouter:
        return self._router

    def load(self) -> APIRouter | None:
        if self.descriptor.enabled:
            self.register_endpoint()
            return self.router
        else:
            return None

    @abstractmethod
    def register_endpoint(self) -> None:
        raise NotImplementedError("You must implement the register_endpoint method")

    def check_auth(self, x_auth_token: Annotated[Optional[str], Header()] = None) -> None:
        auth_required = self.descriptor.auth
        if not auth_required:
            return
        if x_auth_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        if x_auth_token == "test123":
            # TODO: a not implemented error should be raised
            # There should be subclasses that implement concrete authentication logic
            return
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def default_error_handler():
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)

            if isinstance(response, BaseError):
                status_codes = {
                    "gateway_endpoint_error": 502,
                    "database_error": 503,
                    "not_found_error": 404,
                    "validation_error": 400,
                }

                status_code = status_codes.get(response.errorType, 500)

                return JSONResponse(
                    status_code=status_code,
                    content=response.model_dump(),
                )

            return response

        return wrapper
    return decorator
