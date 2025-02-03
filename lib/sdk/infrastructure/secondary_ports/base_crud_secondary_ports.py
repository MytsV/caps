from abc import abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from lib.sdk.core.bac import BaseAbstractClass
from lib.sdk.core.dto import TBaseDTO
from lib.sdk.core.request import BaseIdentifiedRequest, BaseListRequest

TSession = TypeVar("TSession")


class BaseCrudOutputPort(BaseAbstractClass, Generic[TSession]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create(self, session: TSession, request: BaseModel) -> TBaseDTO:
        raise NotImplementedError("You must implement the create method. It should create a new record.")

    @abstractmethod
    def get(self, session: TSession, request: BaseIdentifiedRequest) -> TBaseDTO:
        raise NotImplementedError("You must implement the get method. It should read a single record.")

    @abstractmethod
    def list(self, session: TSession, request: BaseListRequest) -> TBaseDTO:
        raise NotImplementedError(
            "You must implement the list method in your repository. Should 'read' multiple records."
        )

    @abstractmethod
    def update(self, session: TSession, request: BaseIdentifiedRequest) -> TBaseDTO:
        raise NotImplementedError("You must implement the update method in your repository")

    @abstractmethod
    def delete(self, session: TSession, request: BaseIdentifiedRequest) -> TBaseDTO:
        raise NotImplementedError("You must implement the delete method in your repository")
