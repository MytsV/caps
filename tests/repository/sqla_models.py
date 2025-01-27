from lib.infrastructure.repository.sqla.database import Base
from lib.infrastructure.repository.sqla.models import SoftSqlaModelBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from tests.repository.models import PrimitiveCoreModel, CategoryCoreModel, ComposedCoreModel


class PrimitiveSqlaModel(Base, SoftSqlaModelBase):
    __tablename__ = "primitive_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_core_model(self) -> PrimitiveCoreModel:
        return PrimitiveCoreModel(id=self.id, name=self.name)


class CategorySqlaModel(Base, SoftSqlaModelBase):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String, nullable=True)

    def to_core_model(self) -> CategoryCoreModel:
        return CategoryCoreModel(
            id=self.id,
            title=self.title,
            description=self.description
        )


class ComposedSqlaModel(Base, SoftSqlaModelBase):
    __tablename__ = "complex_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    status = Column(String, default="active")

    category = relationship("CategorySqlaModel")

    def to_core_model(self) -> ComposedCoreModel:
        return ComposedCoreModel(
            id=self.id,
            name=self.name,
            description=self.description,
            category=self.category.to_core_model() if self.category else None,
            created_at=self.created_at,
            status=self.status
        )

