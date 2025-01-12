from pydantic import BaseModel, ConfigDict


class BaseEndpointDescriptor(
    BaseModel,
):
    name: str
    description: str
    version: str
    tags: list[str] = []
    enabled: bool = True
    auth: bool = False
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
