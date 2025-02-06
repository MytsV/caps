from abc import abstractmethod
from typing import Generic, TypeVar, Any

from pydantic import BaseModel

from lib.sdk.core.bac import BaseAbstractClass
from lib.sdk.core.dto import TBaseDTO
from lib.sdk.core.request import BaseIdentifiedRequest, BaseListRequest


TCreateRequest = TypeVar("TCreateRequest", bound=BaseModel)
TGetRequest = TypeVar("TGetRequest", bound=BaseIdentifiedRequest)
TListRequest = TypeVar("TListRequest", bound=BaseListRequest)
TUpdateRequest = TypeVar("TUpdateRequest", bound=BaseIdentifiedRequest)
TDeleteRequest = TypeVar("TDeleteRequest", bound=BaseIdentifiedRequest)


class BaseCrudOutputPort(
    BaseAbstractClass, Generic[TCreateRequest, TGetRequest, TListRequest, TUpdateRequest, TDeleteRequest]
):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create(self, request: TCreateRequest) -> TBaseDTO[Any]:
        raise NotImplementedError("You must implement the create method. It should create a new record.")

    @abstractmethod
    def get(self, request: TGetRequest) -> TBaseDTO[Any]:
        raise NotImplementedError("You must implement the get method. It should read a single record.")

    @abstractmethod
    def list(self, request: TListRequest) -> TBaseDTO[Any]:
        raise NotImplementedError(
            "You must implement the list method in your repository. Should 'read' multiple records."
        )

    @abstractmethod
    def update(self, request: TUpdateRequest) -> TBaseDTO[Any]:
        raise NotImplementedError("You must implement the update method in your repository")

    @abstractmethod
    def delete(self, request: TDeleteRequest) -> TBaseDTO[Any]:
        raise NotImplementedError("You must implement the delete method in your repository")
