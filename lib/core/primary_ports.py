from abc import abstractmethod
from typing import Generic
from lib.core.bac import BaseAbstractClass
from lib.core.usecase_models import (
    TBaseErrorResponseModel,
    TBaseRequestModel,
    TBaseResponseModel,
)


class BaseInputPort(BaseAbstractClass, Generic[TBaseRequestModel]):
    """
    Abstract base class for input ports.

    @param requestModel: The request model to use.
    @type requestModel: TBaseRequestModel
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def execute(self, requestModel: TBaseRequestModel) -> None:
        pass


class BaseOutputPort(BaseAbstractClass, Generic[TBaseResponseModel, TBaseErrorResponseModel]):
    """
    Abstract base class for output ports.

    @type-arg TBaseResponseModel: The response model to use.
    @type-arg TBaseErrorResponseModel: The error response model to use.
    @method presentSuccess: Present the success response.
    @param responseModel: The response model to use.
    @type responseModel: TBaseResponseModel
    @method presentError: Present the error response.
    @param errorModel: The error model to use.
    @type errorModel: TBaseErrorResponseModel
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def presentSuccess(self, responseModel: TBaseResponseModel) -> None:
        raise NotImplementedError

    @abstractmethod
    def presentError(self, errorModel: TBaseErrorResponseModel) -> None:
        raise NotImplementedError
