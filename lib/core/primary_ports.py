from abc import abstractmethod
from typing import Generic
from lib.core.bac import BaseAbstractClass
from lib.core.usecase_models import (
    TBaseErrorResponseModel,
    TBaseRequestModel,
    TBaseResponseModel,
)
from lib.core.view_model import TBaseViewModel


class BaseInputPort(BaseAbstractClass, Generic[TBaseRequestModel, TBaseResponseModel, TBaseErrorResponseModel]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def execute(self, requestModel: TBaseRequestModel) -> TBaseResponseModel | TBaseErrorResponseModel:
        raise NotImplementedError("You must implement the execute method in your use case")


class BaseOutputPort(BaseAbstractClass, Generic[TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel]):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def present_success(self, responseModel: TBaseResponseModel) -> TBaseViewModel:
        raise NotImplementedError

    @abstractmethod
    def present_error(self, errorModel: TBaseErrorResponseModel) -> TBaseViewModel:
        raise NotImplementedError
