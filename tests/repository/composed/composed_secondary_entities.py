from typing import List, Generator

from pydantic import BaseModel

from lib.sdk.core.error import BaseError
from lib.sdk.core.request import BaseIdentifiedRequest, BaseListRequest
from lib.sdk.infrastructure.repository.sqla.database import Database

from lib.sdk.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository
from lib.sdk.core.dto import TBaseDTO, TBaseListDTO
from sqlalchemy.orm import Session

from lib.sdk.infrastructure.repository.sqla.utils import sqla_database_context
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


class ComposedRepository(
    DefaultSqlaCrudRepository[
        ComposedCoreModel,
        ComposedCreateRequest,
        ComposedGetRequest,
        ComposedListRequest,
        ComposedUpdateRequest,
        ComposedDeleteRequest,
    ]
):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=ComposedSqlaModel, database=database)

    def create(self, request: ComposedCreateRequest) -> ComposedCreateDTO:
        return super().create(request)

    def get(self, request: ComposedGetRequest) -> ComposedGetDTO:
        return super().get(request)

    def list(self, request: ComposedListRequest) -> ComposedListDTO:
        return super().list(request)

    def update(self, request: ComposedUpdateRequest) -> ComposedUpdateDTO:
        return super().update(request)

    def delete(self, request: ComposedDeleteRequest) -> ComposedDeleteDTO:
        return super().delete(request)


class CategoryCreateRequest(BaseModel):
    title: str
    description: str | None = None


class CategoryGetRequest(BaseIdentifiedRequest):
    pass


class CategoryDeleteRequest(BaseIdentifiedRequest):
    pass


class CategoryUpdateRequest(BaseIdentifiedRequest):
    title: str | None = None
    description: str | None = None


class CategoryListRequest(BaseListRequest):
    pass


class CategoryRepository(
    DefaultSqlaCrudRepository[
        CategoryCoreModel,
        CategoryCreateRequest,
        CategoryGetRequest,
        CategoryListRequest,
        CategoryUpdateRequest,
        CategoryDeleteRequest,
    ]
):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=CategorySqlaModel, database=database)

    def create(self, request: CategoryCreateRequest) -> TBaseDTO[CategoryCoreModel]:
        return super().create(request)

    def get(self, request: CategoryGetRequest) -> TBaseDTO[CategoryCoreModel]:
        return super().get(request)

    def list(self, request: CategoryListRequest) -> TBaseListDTO[List[CategoryCoreModel]]:
        return super().list(request)

    def update(self, request: CategoryUpdateRequest) -> TBaseDTO[CategoryCoreModel]:
        return super().update(request)

    def delete(self, request: CategoryDeleteRequest) -> TBaseDTO[CategoryCoreModel]:
        return super().delete(request)


class ComposedTestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(
        self, repository: ComposedRepository, category_repository: CategoryRepository
    ) -> Generator[None, None, None]:
        yield
        session = repository.session()
        session.query(ComposedSqlaModel).delete()
        session.query(CategorySqlaModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self) -> ComposedRepository:
        return ComposedRepository()

    @pytest.fixture(scope="class")
    def category_repository(self) -> CategoryRepository:
        return CategoryRepository()

    @pytest.fixture
    def category(self, category_repository: CategoryRepository) -> CategoryCoreModel:
        request = CategoryCreateRequest(title="Test Category")
        result = category_repository.create(request)
        if isinstance(result, BaseError):
            raise ValueError(result.message)
        return result.data
