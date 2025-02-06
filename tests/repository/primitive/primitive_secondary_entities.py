from typing import List, Generator

from pydantic import BaseModel

from lib.sdk.core.request import BaseIdentifiedRequest, BaseListRequest
from lib.sdk.infrastructure.repository.sqla.database import Database

from lib.sdk.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository
from lib.sdk.core.dto import TBaseDTO, TBaseListDTO
from sqlalchemy.orm import Session

from lib.sdk.infrastructure.repository.sqla.utils import sqla_database_context
from tests.repository.models import PrimitiveCoreModel
from tests.repository.sqla_models import PrimitiveSqlaModel

import pytest

PrimitiveCreateDTO = TBaseDTO[PrimitiveCoreModel]
PrimitiveGetDTO = TBaseDTO[PrimitiveCoreModel]
PrimitiveListDTO = TBaseListDTO[List[PrimitiveCoreModel]]
PrimitiveUpdateDTO = TBaseDTO[PrimitiveCoreModel]
PrimitiveDeleteDTO = TBaseDTO[PrimitiveCoreModel]


class PrimitiveCreateRequest(BaseModel):
    name: str


class PrimitiveGetRequest(BaseIdentifiedRequest):
    pass


class PrimitiveDeleteRequest(BaseIdentifiedRequest):
    pass


class PrimitiveUpdateRequest(BaseIdentifiedRequest):
    name: str


class PrimitiveListRequest(BaseListRequest):
    pass


class PrimitiveRepository(DefaultSqlaCrudRepository[
                              PrimitiveCoreModel,
                              PrimitiveCreateRequest,
                              PrimitiveGetRequest,
                              PrimitiveListRequest,
                              PrimitiveUpdateRequest,
                              PrimitiveDeleteRequest
                          ]):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=PrimitiveSqlaModel, database=database)

    def create(self, request: PrimitiveCreateRequest) -> PrimitiveCreateDTO:
        return super().create(request)

    def get(self, request: PrimitiveGetRequest) -> PrimitiveGetDTO:
        return super().get(request)

    def list(self, request: PrimitiveListRequest) -> PrimitiveListDTO:
        return super().list(request)

    def update(self, request: PrimitiveUpdateRequest) -> PrimitiveUpdateDTO:
        return super().update(request)

    def delete(self, request: PrimitiveDeleteRequest) -> PrimitiveDeleteDTO:
        return super().delete(request)


class PrimitiveTestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository: PrimitiveRepository) -> Generator[None, None, None]:
        yield
        session = repository.session()
        session.query(PrimitiveSqlaModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self) -> PrimitiveRepository:
        return PrimitiveRepository()
