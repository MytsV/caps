from typing import List

from pydantic import BaseModel

from lib.core.models import BaseCoreModel
from lib.core.request import BaseIdentifiedRequest, BaseListRequest
from lib.infrastructure.repository.sqla.database import Base
from lib.infrastructure.repository.sqla.models import SoftSqlaModelBase
from sqlalchemy import Column, Integer, String
import pytest

from lib.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository
from lib.core.dto import TBaseDTO
from sqlalchemy.orm import Session

from lib.infrastructure.repository.sqla.utils import sqla_session_context


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

    def to_core_model(self) -> TestCoreModel:
        return TestCoreModel(id=self.id, name=self.name)


TestCreateDTO = TBaseDTO[TestCoreModel]
TestGetDTO = TBaseDTO[TestCoreModel]
TestListDTO = TBaseDTO[List[TestCoreModel]]
TestUpdateDTO = TBaseDTO[TestCoreModel]
TestDeleteDTO = TBaseDTO[TestCoreModel]


class TestCreateRequest(BaseModel):
    name: str


class TestGetRequest(BaseIdentifiedRequest):
    pass


class TestDeleteRequest(BaseIdentifiedRequest):
    pass


class TestUpdateRequest(BaseIdentifiedRequest):
    name: str


class TestListRequest(BaseListRequest):
    pass


class TestRepository(DefaultSqlaCrudRepository[TestCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=TestSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: TestCreateRequest) -> TestCreateDTO:
        return super().create(session, request)

    @sqla_session_context()
    def get(self, session: Session, request: TestGetRequest) -> TestGetDTO:
        return super().get(session, request)

    @sqla_session_context()
    def list(self, session: Session, request: TestListRequest) -> TestListDTO:
        return super().list(session, request)

    @sqla_session_context()
    def update(self, session: Session, request: TestUpdateRequest) -> TestUpdateDTO:
        return super().update(session, request)

    @sqla_session_context()
    def delete(self, session: Session, request: TestDeleteRequest) -> TestDeleteDTO:
        return super().delete(session, request)


class TestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository):
        yield
        session = repository.session()
        session.query(TestSqlaModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return TestRepository()
