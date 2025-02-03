from typing import Literal, TypeVar
from pydantic import BaseModel


class BaseRequestModel(BaseModel):
    pass


class BaseAuthenticatedRequestModel(BaseRequestModel):
    user_id: int
    auth_token: str


class BaseResponseModel(BaseModel):
    """
    Base response model for all use cases.

    @param status: The status of the response. Equals True.
    """

    status: Literal[True] = True


class BaseErrorResponseModel(BaseModel):
    status: Literal[False] = False
    code: int
    message: str


TBaseRequestModel = TypeVar("TBaseRequestModel", bound=BaseRequestModel)

TBaseAuthenticatedRequestModel = TypeVar("TBaseAuthenticatedRequestModel", bound=BaseAuthenticatedRequestModel)

TBaseRequestModelOrBaseAuthenticatedRequestModel = TypeVar(
    "TBaseRequestModelOrBaseAuthenticatedRequestModel", bound=BaseRequestModel | BaseAuthenticatedRequestModel
)

TBaseResponseModel = TypeVar("TBaseResponseModel", bound=BaseResponseModel)

TBaseErrorResponseModel = TypeVar("TBaseErrorResponseModel", bound=BaseErrorResponseModel)
