from abc import abstractmethod
from typing import Generic, TypeVar
from pydantic import BaseModel
from lib.core.bac import BaseAbstractClass
from lib.core.dto import TBaseDTO
from lib.core.models import TBaseSDKModel



class BaseCRUDDTORequestModel(BaseModel):
    """
    A base class for the CRUD DTO request model.
    """
    pass

TBaseCRUDDTORequestModel = TypeVar("TBaseCRUDDTORequestModel", bound=BaseCRUDDTORequestModel)


TSession = TypeVar("TSession")

class BaseCRUDRepositoryOutputPort(BaseAbstractClass, Generic[TSession, TBaseSDKModel]):
    """
    A base class for the CRUD repository output port.
    """
    class __TCreateModelDTORequest:
        model: TBaseSDKModel
        

    
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def create[T](self, session: TSession, request: __TCreateModelDTORequest) -> TCreateModelDTO[TBaseSDKModel]:
        raise NotImplementedError("You must implement the create method in your repository")
    
    @abstractmethod
    def get[T](self, session: TSession, request: TBaseCRUDDTORequestModel) -> TBaseDTO[T]:
        raise NotImplementedError("You must implement the get method in your repository. Should 'read' a single record.")

    @abstractmethod
    def list[T](self, session: TSession, request: TBaseCRUDDTORequestModel) -> TBaseDTO[T]:
        raise NotImplementedError("You must implement the list method in your repository. Should 'read' multiple records.")
    
    @abstractmethod
    def update[T](self, session: TSession, request: TBaseCRUDDTORequestModel) -> TBaseDTO[T]:
        raise NotImplementedError("You must implement the update method in your repository")
    
    @abstractmethod
    def delete[T](self, session: TSession, request: TBaseCRUDDTORequestModel) -> TBaseDTO[T]:
        raise NotImplementedError("You must implement the delete method in your repository")