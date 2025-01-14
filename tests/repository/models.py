from lib.core.models import BaseCoreModel
from lib.infrastructure.repository.sqla.database import Base
from lib.infrastructure.repository.sqla.models import SoftSqlaModelBase
from sqlalchemy import Column, Integer, String
import pytest

from lib.infrastructure.repository.sqla.sqla_crud_repository import BaseSqlaCrudRepository


class TestCoreModel(BaseCoreModel):
    id: int | None = None
    name: str


class TestPartialCoreModel(BaseCoreModel):
    name: str
    extra_field: str | None = None


class TestSqlaModel(Base, SoftSqlaModelBase):
    __tablename__ = "test_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_sdk_model(self) -> TestCoreModel:
        return TestCoreModel(id=self.id, name=self.name)


class TestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository):
        yield
        session = repository.session()
        session.query(TestSqlaModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return BaseSqlaCrudRepository(TestSqlaModel)
