import json
from typing import TypeVar
from pydantic import BaseModel


class BaseCoreModel(BaseModel):
    """
    A base SDK model class for the project.
    """

    def to_json(cls) -> str:
        """
        Dumps the model to a json formatted string. Wrapper around pydantic's model_dump_json method: in case they decide to deprecate it, we only refactor here.
        """
        return cls.model_dump_json()

    def __str__(self) -> str:
        return self.to_json()

    def pretty_print_json(self) -> None:
        """
        Pretty prints a JSON dictionary with 2-space indentation.
        :param json_data: JSON data in dictionary format or JSON string.
        """
        json_s = self.to_json()
        json_data = json.loads(json_s)
        print(json.dumps(json_data, indent=2))


TBaseCoreModel = TypeVar("TBaseCoreModel", bound=BaseCoreModel)

TID = TypeVar("TID", str, int)
