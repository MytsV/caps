"""
This module defines the PresenterResponse class.

@author:
@version: 1.0
"""

from abc import ABC, abstractmethod
from typing import TypeVar

from lib.view_model import TBaseViewModel

TPresenterResponse = TypeVar("TPresenterResponse", bound="PresenterResponse")


class PresenterResponse(ABC):
    """
    Abstract base class for presenter response objects.
    This needs to be implemented by a web framework, for example.
    """

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def present(self, view_model: TBaseViewModel) -> None:
        """
        Presents the given view model to the user.
        For a web framework, you would check the status of the view model and
        return the appropriate HTTP status code.

        :param view_model: The view model to present.
        :type view_model: TResponse
        """
        raise NotImplementedError
