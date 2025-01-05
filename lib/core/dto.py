from typing import TypeVar
from pydantic import BaseModel


class BaseDTO(BaseModel):
    status: bool
    errorCode: int
    errorName: str
    errorMessage: str


TBaseDTO = TypeVar("TBaseDTO", bound=BaseDTO)
