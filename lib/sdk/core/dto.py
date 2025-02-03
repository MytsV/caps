from typing import Literal, TypeVar

from lib.sdk.core.models import BaseCoreModel
from lib.sdk.core.error import BaseError


class SuccessDTO[T](BaseCoreModel):
    """
    A success DTO class for the project.

    @param success: The status of the operation, with True meaning 'success'
    @type success: Literal[True]
    @param data: The data of the operation.
    @type data: T
    """

    success: Literal[True] = True
    data: T


class SuccessListDTO[T](SuccessDTO[T]):
    has_next_page: bool | None = None


type TBaseDTO[T] = SuccessDTO[T] | BaseError

type TBaseListDTO[T] = SuccessListDTO[T] | BaseError
