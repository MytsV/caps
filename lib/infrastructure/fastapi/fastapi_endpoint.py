from abc import ABC, abstractmethod
from enum import Enum
from typing import Annotated, Any, Dict, Generic, List, Callable, TypeVar, Union
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import ValidationError
from lib.infrastructure.controller import BaseController, TBaseControllerParameters
from lib.core.dto import SuccessDTO
from lib.core.error import BaseError
from lib.infrastructure.config.feature_descriptor import BaseFeatureDescriptor
import logging

from lib.core.models import TBaseCoreModel
from lib.infrastructure.secondary_ports import (
    TBaseCrudRequest,
    DeleteRequest,
    DeletedDTO,
    UpdatedDTO,
    UpdateRequest,
    BaseCrudRequest,
    GetRequest,
    CreateRequest,
    CreatedDTO,
)
from lib.infrastructure.repository.sqla.sqla_crud_repository import BaseSqlaCrudRepository

logger = logging.getLogger(__name__)

from lib.core.view_model import (
    BaseViewModel,
    TBaseViewModel,
)

from fastapi import status, Body, HTTPException
from functools import wraps


class BaseFastAPIEndpoint(ABC, Generic[TBaseControllerParameters, TBaseViewModel]):
    def __init__(
        self,
        descriptor: BaseFeatureDescriptor,
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
    def descriptor(self) -> BaseFeatureDescriptor:
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

    def check_auth(self, x_auth_token: Annotated[str, Header()]) -> None:
        auth_required = self.descriptor.auth
        if not auth_required:
            return
        if x_auth_token is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
        if x_auth_token == "test123":
            return
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


class FastAPIControllerEndpoint(BaseFastAPIEndpoint[TBaseControllerParameters, TBaseViewModel]):
    def __init__(
        self,
        controller: BaseController[TBaseControllerParameters, Any, Any, Any, TBaseViewModel],
        descriptor: BaseFeatureDescriptor,
        responses: Dict[int | str, dict[str, Any]],
    ) -> None:
        super().__init__(descriptor, responses)
        self._controller = controller
        self.prefix += "/controller"

    @property
    def controller(
        self,
    ) -> BaseController[TBaseControllerParameters, Any, Any, Any, TBaseViewModel]:
        return self._controller

    def execute(self, controller_parameters: TBaseControllerParameters) -> TBaseViewModel:
        try:
            view_model = self.controller.execute(controller_parameters)
            if view_model is None:
                raise HTTPException(status_code=500, detail="Internal Server Error. Did not receive a view model")
            else:
                return view_model
        except ValidationError as ve:
            return self.controller.presenter.present_error(
                BaseViewModel(
                    status=False,
                    code=400,
                    errorCode=400,
                    errorMessage=f"ValidationError: {ve}",
                    errorName="Controller Parameter Validation Error",
                    errorType=f"ControllerParameterValidationError",
                )
            )
        except Exception as e:
            logger.error(f"Critical Error in {self.name} endpoint. See the following exception: {e}")
            raise e

    @abstractmethod
    def register_endpoint(self) -> None:
        raise NotImplementedError(
            "You must implement the register_endpoint method in your Controller endpoint subclass"
        )


ResponseType = TypeVar("ResponseType", bound=Union[CreatedDTO, SuccessDTO, UpdatedDTO, DeletedDTO, BaseError])


async def verify_auth_token(x_auth_token: str = Header(None)):
    if x_auth_token is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return x_auth_token


def handle_repository_errors(func: Callable[..., ResponseType]) -> Callable[..., ResponseType]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> ResponseType:
        result = await func(*args, **kwargs)
        if isinstance(result, BaseError):
            error_code = 500
            if result.errorType == "not_found":
                error_code = 404
            elif result.errorType == "database_error":
                error_code = 500
            elif result.errorType == "invalid_field":
                error_code = 400

            # TODO: pass the error fully in the response body, not just in a detail attribute
            raise HTTPException(status_code=error_code, detail=result.model_dump())
        return result

    return wrapper


class FastAPICrudRepositoryEndpoint(BaseFastAPIEndpoint[TBaseCrudRequest, TBaseViewModel]):
    def __init__(
        self,
        repository: BaseSqlaCrudRepository,
        descriptor: BaseFeatureDescriptor,
        responses: Dict[int | str, dict[str, Any]],
    ) -> None:
        super().__init__(descriptor, responses)
        self._repository = repository
        self.prefix += "/repository"

    def register_endpoint(self) -> None:
        @self.router.post(
            f"{self.prefix}/{self.name}",
            response_model=CreatedDTO[TBaseCoreModel],
            responses=self.responses,
            dependencies=[Depends(verify_auth_token)],
        )
        @handle_repository_errors
        async def create_item(request: CreateRequest = Body()) -> CreatedDTO[TBaseCoreModel]:
            return self._repository.create(request)

        @self.router.get(
            f"{self.prefix}/{self.name}/{{item_id}}",
            response_model=SuccessDTO[TBaseCoreModel],
            responses=self.responses,
            dependencies=[Depends(verify_auth_token)],
        )
        @handle_repository_errors
        async def get_item(item_id: int) -> SuccessDTO[TBaseCoreModel]:
            return self._repository.get(GetRequest(id=item_id))

        @self.router.get(
            f"{self.prefix}/{self.name}",
            response_model=SuccessDTO[List[TBaseCoreModel]],
            responses=self.responses,
            dependencies=[Depends(verify_auth_token)],
        )
        @handle_repository_errors
        async def list_items() -> SuccessDTO[List[TBaseCoreModel]]:
            return self._repository.list(BaseCrudRequest())

        @self.router.put(
            f"{self.prefix}/{self.name}",
            response_model=UpdatedDTO[TBaseCoreModel],
            responses=self.responses,
            dependencies=[Depends(verify_auth_token)],
        )
        @handle_repository_errors
        async def update_item(request: UpdateRequest) -> UpdatedDTO[TBaseCoreModel]:
            return self._repository.update(request)

        @self.router.delete(
            f"{self.prefix}/{self.name}/{{item_id}}",
            response_model=DeletedDTO[TBaseCoreModel],
            responses=self.responses,
            dependencies=[Depends(verify_auth_token)],
        )
        @handle_repository_errors
        async def delete_item(item_id: int) -> DeletedDTO[TBaseCoreModel]:
            return self._repository.delete(DeleteRequest(id=item_id))
