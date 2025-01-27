from datetime import datetime

from lib.core.models import BaseCoreModel


class PrimitiveCoreModel(BaseCoreModel):
    id: int | None = None
    name: str


class CategoryCoreModel(BaseCoreModel):
    id: int | None = None
    title: str
    description: str | None = None


class ComposedCoreModel(BaseCoreModel):
    id: int | None = None
    name: str
    description: str | None = None
    category: CategoryCoreModel
    created_at: datetime
    status: str = "active"

