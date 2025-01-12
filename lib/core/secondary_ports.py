from abc import abstractmethod
from datetime import datetime
from typing import Generic, TypeVar, List
from pydantic import BaseModel
from lib.core.bac import BaseAbstractClass
from lib.core.dto import TBaseDTO, SuccessDTO
from lib.core.error import BaseError
from lib.core.models import TID, TEntitySDKModel, TBaseSDKModel


class BaseCrudRequest(BaseModel):
    """
    A base class for the CRUD DTO request model.
    """

    pass


TBaseCrudRequest = TypeVar("TBaseCrudRequest", bound=BaseCrudRequest)

TSession = TypeVar("TSession")


class CreateRequest(BaseCrudRequest):
    data: TBaseSDKModel


TCreateRequest = TypeVar("TCreateRequest", bound=CreateRequest)


class UpdateRequest(BaseCrudRequest):
    id: TID
    data: TBaseSDKModel


TUpdateRequest = TypeVar("TUpdateRequest", bound=UpdateRequest)


class DeleteRequest(BaseCrudRequest):
    id: TID


TDeleteRequest = TypeVar("TDeleteRequest", bound=DeleteRequest)


class GetRequest(BaseCrudRequest):
    id: TID


TGetRequest = TypeVar("TGetRequest", bound=GetRequest)


class CreatedData(BaseModel, Generic[TEntitySDKModel]):
    data: TEntitySDKModel
    created_at: datetime


class CreatedDTO(SuccessDTO[CreatedData[TEntitySDKModel]], Generic[TEntitySDKModel]):
    pass


class UpdatedData(BaseModel, Generic[TEntitySDKModel]):
    data: TEntitySDKModel
    updated_at: datetime


class UpdatedDTO(SuccessDTO[UpdatedData[TEntitySDKModel]], Generic[TEntitySDKModel]):
    pass


class DeletedData(BaseModel, Generic[TEntitySDKModel]):
    id: TID
    deleted_at: datetime


class DeletedDTO(SuccessDTO[DeletedData[TEntitySDKModel]], Generic[TEntitySDKModel]):
    pass


class BaseCrudRepositoryOutputPort(BaseAbstractClass, Generic[TSession, TEntitySDKModel]):
    """
    A base class for the CRUD repository output port.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create(self, session: TSession, request: TCreateRequest) -> CreatedDTO[TEntitySDKModel] | BaseError:
        raise NotImplementedError("You must implement the create method in your repository")

    @abstractmethod
    def get(self, session: TSession, request: TGetRequest) -> TBaseDTO[TEntitySDKModel]:
        raise NotImplementedError(
            "You must implement the get method in your repository. Should 'read' a single record."
        )

    @abstractmethod
    def list(self, session: TSession, request: TBaseCrudRequest) -> TBaseDTO[List[TEntitySDKModel]]:
        raise NotImplementedError(
            "You must implement the list method in your repository. Should 'read' multiple records."
        )

    @abstractmethod
    def update(self, session: TSession, request: TUpdateRequest) -> UpdatedDTO[TEntitySDKModel] | BaseError:
        raise NotImplementedError("You must implement the update method in your repository")

    @abstractmethod
    def delete(self, session: TSession, request: TDeleteRequest) -> CreatedDTO[TEntitySDKModel] | BaseError:
        raise NotImplementedError("You must implement the delete method in your repository")
