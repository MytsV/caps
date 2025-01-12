from lib.core.models import BaseSDKModel, EntitySDKModel
from lib.infrastructure.repository.sqla.database import Base
from lib.infrastructure.repository.sqla.models import SoftModelBase
from sqlalchemy import Column, Integer, String
import pytest

from lib.infrastructure.repository.sqla.sqla_crud_repository import BaseSqlaCrudRepository


class TestSDKModel(EntitySDKModel):
    id: int | None = None
    name: str


class TestPartialSDKModel(BaseSDKModel):
    name: str
    extra_field: str | None = None


class TestSQLModel(Base, SoftModelBase):
    __tablename__ = "test_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_sdk_model(self) -> TestSDKModel:
        return TestSDKModel(id=self.id, name=self.name)


class TestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository):
        yield
        session = repository.session()
        session.query(TestSQLModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return BaseSqlaCrudRepository(TestSQLModel)
