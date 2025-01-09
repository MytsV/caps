from abc import abstractmethod
from typing import Generic

from pydantic import ValidationError
from lib.core.primary_ports import BaseOutputPort
from lib.core.usecase_models import TBaseErrorResponseModel, TBaseResponseModel, BaseErrorResponseModel
from lib.core.view_model import TBaseViewModel


class BasePresenter(
    BaseOutputPort[TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel],
    Generic[TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel],
):
    def present_success(self, response: TBaseResponseModel) -> TBaseViewModel:
        try:
            view_model = self.convert_response_to_view_model(response)
            return view_model
        except ValidationError as error:
            return self.convert_error_response_to_view_model(
                BaseErrorResponseModel(  # type: ignore
                    code=500,
                    message="ValidationError",
                )
            )

    def present_error(self, response: TBaseErrorResponseModel) -> TBaseViewModel:
        return self.convert_error_response_to_view_model(response)

    @abstractmethod
    def convert_error_response_to_view_model(self, response: TBaseErrorResponseModel) -> TBaseViewModel:
        raise NotImplementedError(
            "You must implement the convert_error_response_to_view_model method in your presenter"
        )

    @abstractmethod
    def convert_response_to_view_model(self, response: TBaseResponseModel) -> TBaseViewModel:
        raise NotImplementedError("You must implement the convert_response_to_view_model method in your presenter")
