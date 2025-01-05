"""
This module defines the BaseViewModel class.

@author:
@version: 1.0
"""

from typing import TypeVar
from pydantic import BaseModel


class BaseViewModel(BaseModel):
    """
    A base view model class that contains common properties for all view models.

    :status (bool): The status of the view model.
    :errorName (str, optional): The name of the error, if any.
    :errorMessage (str, optional): The error message, if any.
    """

    status: bool
    errorName: str | None = None
    errorMessage: str | None = None


TBaseViewModel = TypeVar("TBaseViewModel", bound=BaseViewModel)
