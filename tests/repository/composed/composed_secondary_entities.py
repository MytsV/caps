from typing import List

from pydantic import BaseModel

from lib.core.request import BaseIdentifiedRequest, BaseListRequest

from lib.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository
from lib.core.dto import TBaseDTO, TBaseListDTO
from sqlalchemy.orm import Session

from lib.infrastructure.repository.sqla.utils import sqla_session_context
import pytest

from tests.repository.models import ComposedCoreModel, CategoryCoreModel
from tests.repository.sqla_models import ComposedSqlaModel, CategorySqlaModel

ComposedCreateDTO = TBaseDTO[ComposedCoreModel]
ComposedGetDTO = TBaseDTO[ComposedCoreModel]
ComposedListDTO = TBaseListDTO[List[ComposedCoreModel]]
ComposedUpdateDTO = TBaseDTO[ComposedCoreModel]
ComposedDeleteDTO = TBaseDTO[ComposedCoreModel]

class ComposedCreateRequest(BaseModel):
    name: str
    description: str | None = None
    category_id: int
    status: str = "active"


class ComposedGetRequest(BaseIdentifiedRequest):
    pass


class ComposedDeleteRequest(BaseIdentifiedRequest):
    pass


class ComposedUpdateRequest(BaseIdentifiedRequest):
    name: str | None = None
    description: str | None = None
    category_id: int | None = None
    status: str | None = None


class ComposedListRequest(BaseListRequest):
    name: str | None = None
    status: str | None = None

class ComposedRepository(DefaultSqlaCrudRepository[ComposedCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=ComposedSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: ComposedCreateRequest) -> ComposedCreateDTO:
        return super().create(session, request)

    @sqla_session_context()
    def get(self, session: Session, request: ComposedGetRequest) -> ComposedGetDTO:
        return super().get(session, request)

    @sqla_session_context()
    def list(self, session: Session, request: ComposedListRequest) -> ComposedListDTO:
        return super().list(session, request)

    @sqla_session_context()
    def update(self, session: Session, request: ComposedUpdateRequest) -> ComposedUpdateDTO:
        return super().update(session, request)

    @sqla_session_context()
    def delete(self, session: Session, request: ComposedDeleteRequest) -> ComposedDeleteDTO:
        return super().delete(session, request)


class CategoryCreateRequest(BaseModel):
    title: str
    description: str | None = None


class CategoryRepository(DefaultSqlaCrudRepository[CategoryCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=CategorySqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: CategoryCreateRequest) -> TBaseDTO[CategoryCoreModel]:
        return super().create(session, request)


class ComposedTestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository, category_repository):
        yield
        session = repository.session()
        session.query(ComposedSqlaModel).delete()
        session.query(CategorySqlaModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return ComposedRepository()

    @pytest.fixture(scope="class")
    def category_repository(self):
        return CategoryRepository()

    @pytest.fixture
    def category(self, category_repository):
        request = CategoryCreateRequest(title="Test Category")
        result = category_repository.create(request)
        return result.data
