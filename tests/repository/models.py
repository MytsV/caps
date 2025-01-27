from lib.core.models import BaseCoreModel


class PrimitiveCoreModel(BaseCoreModel):
    id: int | None = None
    name: str
