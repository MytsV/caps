"""
This module defines the BasePresenter class.

@author:
@version: 1.0
"""

from abc import abstractmethod
from typing import Generic
from lib.core.primary_ports import BaseOutputPort
from lib.core.response import TPresenterResponse
from lib.core.usecase_models import TBaseErrorResponseModel, TBaseResponseModel
from lib.core.view_model import TBaseViewModel


class BasePresenter(
    BaseOutputPort[TBaseResponseModel, TBaseErrorResponseModel],
    Generic[TBaseResponseModel, TBaseErrorResponseModel, TBaseViewModel],
):
    """
    Abstract base class for presenters.

    @param response: The presenter response object to use.
    :type response: TPresenterResponse
    """

    def __init__(self, response: TPresenterResponse) -> None:
        super().__init__()
        self.response: TPresenterResponse = response

    @abstractmethod
    def convertResponseToViewModel(self, responseModel: TBaseResponseModel) -> TBaseViewModel:
        """
        Converts the given response model to a view model.

        :param responseModel: The response model to convert.
        :type responseModel: TBaseResponseModel
        :return: The resulting view model.
        :rtype: TBaseViewModel
        """
        raise NotImplementedError

    @abstractmethod
    def convertErrorToViewModel(self, errorModel: TBaseErrorResponseModel) -> TBaseViewModel:
        """
        Converts the given error model to a view model.

        :param errorModel: The error model to convert.
        :type errorModel: TBaseErrorResponseModel
        :return: The resulting view model.
        :rtype: TBaseViewModel
        """
        raise NotImplementedError

    def presentSuccess(self, responseModel: TBaseResponseModel) -> None:
        """
        Presents the given response model as a success.

        :param responseModel: The response model to present.
        :type responseModel: TBaseResponseModel
        """
        view_model: TBaseViewModel = self.convertResponseToViewModel(responseModel)
        self.response.present(view_model)

    def presentError(self, errorModel: TBaseErrorResponseModel) -> None:
        """
        Presents the given error model as an error.

        :param errorModel: The error model to present.
        :type errorModel: TBaseErrorResponseModel
        """
        view_model: TBaseViewModel = self.convertErrorToViewModel(errorModel)
        self.response.present(view_model)
