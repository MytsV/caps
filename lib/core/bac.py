from abc import ABC
import logging


class BaseAbstractClass(ABC):
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def __repr__(self) -> str:
        return f"{__name__}"

    def __str__(self) -> str:
        return f"{__name__}"
