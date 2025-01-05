from abc import abstractmethod
from typing import Generic
from lib.core.dto import TBaseDTO
from lib.core.primary_ports import BaseInputPort, BaseOutputPort
from lib.core.usecase_models import (
    BaseErrorResponseModel,
    TBaseAuthenticatedRequestModel,
    TBaseErrorResponseModel,
    TBaseRequestModel,
    TBaseResponseModel,
)


class BaseUseCase(
    BaseInputPort[TBaseRequestModel | TBaseAuthenticatedRequestModel],
    Generic[TBaseRequestModel, TBaseAuthenticatedRequestModel, TBaseResponseModel, TBaseErrorResponseModel],
):
    def __init__(self, presenter: BaseOutputPort[TBaseResponseModel, TBaseErrorResponseModel]) -> None:
        super().__init__()
        self.presenter: BaseOutputPort[TBaseResponseModel, TBaseErrorResponseModel] = presenter

    @abstractmethod
    def validate_request_model(self, requestModel: TBaseRequestModel | TBaseAuthenticatedRequestModel) -> None:
        raise NotImplementedError

    @abstractmethod
    def execute(self, requestModel: TBaseRequestModel | TBaseAuthenticatedRequestModel) -> None:
        raise NotImplementedError


class BaseSingleDTOUseCase(
    BaseUseCase[TBaseRequestModel, TBaseAuthenticatedRequestModel, TBaseResponseModel, TBaseErrorResponseModel],
    Generic[TBaseRequestModel, TBaseAuthenticatedRequestModel, TBaseResponseModel, TBaseErrorResponseModel, TBaseDTO],
):
    def __init__(self, presenter: BaseOutputPort[TBaseResponseModel, TBaseErrorResponseModel]) -> None:
        super().__init__(presenter)

    @abstractmethod
    def make_dto_request(self, requestModel: TBaseRequestModel | TBaseAuthenticatedRequestModel) -> TBaseDTO:
        raise NotImplementedError

    @abstractmethod
    def handle_dto_error(self, dto: TBaseDTO) -> TBaseErrorResponseModel:
        raise NotImplementedError

    @abstractmethod
    def process_dto(self, dto: TBaseDTO) -> TBaseResponseModel | TBaseErrorResponseModel:
        raise NotImplementedError

    def execute(self, requestModel: TBaseRequestModel | TBaseAuthenticatedRequestModel) -> None:
        self.validate_request_model(requestModel)
        dto: TBaseDTO = self.make_dto_request(requestModel)
        if dto.status == False:
            errorModel: TBaseErrorResponseModel = self.handle_dto_error(dto)
            self.presenter.presentError(errorModel)
        else:
            responseModel: TBaseResponseModel | TBaseErrorResponseModel = self.process_dto(dto)
            if responseModel.status == False:
                self.presenter.presentError(responseModel)  # type: ignore
            else:
                self.presenter.presentSuccess(responseModel)  # type: ignore
