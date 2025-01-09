from typing import Literal, TypeVar

from lib.core.models import BaseSDKModel
from lib.core.error import BaseError


class SuccessDTO[T](BaseSDKModel):
    """
    A success DTO class for the project.

    @param success: The status of the operation, with True meaning 'success'
    @type success: Literal[True]
    @param data: The data of the operation.
    @type data: T
    """

    success: Literal[True] = True
    data: T


type TBaseDTO[T] = SuccessDTO[T] | BaseError
