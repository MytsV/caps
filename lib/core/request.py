from pydantic import BaseModel

type TID = int | str


class BaseIdentifiedRequest(BaseModel):
    id: TID


class BaseListRequest(BaseModel):
    page: int | None = None
    page_size: int | None = None
