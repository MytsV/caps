from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel
from lib.sdk.infrastructure.presenter import BasePresenter
from lib.sdk.core.usecase import BaseUseCase

from lib.sdk.core.usecase_models import (
    TBaseRequestModel,
    TBaseErrorResponseModel,
    TBaseRequestModel,
    TBaseResponseModel,
    BaseErrorResponseModel,
)
from lib.sdk.core.view_model import TBaseViewModel


class BaseControllerParameters(BaseModel):
    pass


TBaseControllerParameters = TypeVar("TBaseControllerParameters", bound=BaseControllerParameters)

T = TypeVar("T")


class BaseController(
    ABC,
    Generic[TBaseControllerParameters, TBaseRequestModel, TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel],
):
    def __init__(
        self,
        usecase: BaseUseCase[TBaseRequestModel, TBaseResponseModel, TBaseErrorResponseModel],
        presenter: BasePresenter[TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel],
    ) -> None:
        super().__init__()
        self._presenter = presenter
        self._usecase = usecase

    @property
    def usecase(self) -> BaseUseCase[TBaseRequestModel, TBaseResponseModel, TBaseErrorResponseModel]:
        return self._usecase

    @property
    def presenter(self) -> BasePresenter[TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel]:
        return self._presenter

    @abstractmethod
    def create_request(self, parameters: TBaseControllerParameters | None) -> TBaseRequestModel:
        raise NotImplementedError("You must implement the create_request method in your controller")

    def execute(self, parameters: TBaseControllerParameters | None) -> TBaseViewModel | None:
        request_model = self.create_request(parameters)
        response_model = self.usecase.execute(request_model)
        if isinstance(response_model, BaseErrorResponseModel):
            return self.presenter.present_error(response_model)  # type: ignore
        else:
            return self.presenter.present_success(response_model)
