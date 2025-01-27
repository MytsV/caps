from lib.infrastructure.repository.sqla.database import Base
from lib.infrastructure.repository.sqla.models import SoftSqlaModelBase
from sqlalchemy import Column, Integer, String
from tests.repository.models import PrimitiveCoreModel


class PrimitiveSqlaModel(Base, SoftSqlaModelBase):
    __tablename__ = "primitive_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_core_model(self) -> PrimitiveCoreModel:
        return PrimitiveCoreModel(id=self.id, name=self.name)