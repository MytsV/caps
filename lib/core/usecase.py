from abc import abstractmethod
from typing import Generic, TypeVar
from lib.core.dto import TBaseDTO
from lib.core.primary_ports import BaseInputPort
from lib.core.usecase_models import (
    TBaseRequestModelOrBaseAuthenticatedRequestModel,
    TBaseErrorResponseModel,
    TBaseRequestModel,
    TBaseResponseModel,
)
from lib.core.view_model import TBaseViewModel

T = TypeVar("T")


class BaseUseCase(
    BaseInputPort[TBaseRequestModelOrBaseAuthenticatedRequestModel, TBaseResponseModel, TBaseErrorResponseModel],
    Generic[TBaseRequestModelOrBaseAuthenticatedRequestModel, TBaseResponseModel, TBaseErrorResponseModel],
):
    @abstractmethod
    def validate_request_model(self, request: TBaseRequestModelOrBaseAuthenticatedRequestModel) -> None:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self, request: TBaseRequestModelOrBaseAuthenticatedRequestModel
    ) -> TBaseResponseModel | TBaseErrorResponseModel:
        raise NotImplementedError


class BaseSingleDTOUseCase(
    BaseUseCase[TBaseRequestModelOrBaseAuthenticatedRequestModel, TBaseResponseModel, TBaseErrorResponseModel],
    Generic[
        TBaseRequestModel,
        TBaseRequestModelOrBaseAuthenticatedRequestModel,
        TBaseResponseModel,
        TBaseErrorResponseModel,
        T,
    ],
):
    @abstractmethod
    def make_dto_request(self, request: TBaseRequestModelOrBaseAuthenticatedRequestModel) -> TBaseDTO[T]:
        raise NotImplementedError

    @abstractmethod
    def handle_dto_error(self, dto: TBaseDTO[T]) -> TBaseErrorResponseModel:
        raise NotImplementedError

    @abstractmethod
    def process_dto(self, dto: TBaseDTO[T]) -> TBaseResponseModel | TBaseErrorResponseModel:
        raise NotImplementedError

    @abstractmethod
    def execute(
        self, request: TBaseRequestModelOrBaseAuthenticatedRequestModel
    ) -> TBaseResponseModel | TBaseErrorResponseModel:
        """
        A base class for use case

        Raises:
            NotImplementedError: _description_
        """
        raise NotImplementedError("You must implement the execute method in your use case")
