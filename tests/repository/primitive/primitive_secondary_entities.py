from typing import List

from pydantic import BaseModel

from lib.core.request import BaseIdentifiedRequest, BaseListRequest

from lib.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository
from lib.core.dto import TBaseDTO, TBaseListDTO
from sqlalchemy.orm import Session

from lib.infrastructure.repository.sqla.utils import sqla_session_context
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


class PrimitiveRepository(DefaultSqlaCrudRepository[PrimitiveCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=PrimitiveSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: PrimitiveCreateRequest) -> PrimitiveCreateDTO:
        return super().create(session, request)

    @sqla_session_context()
    def get(self, session: Session, request: PrimitiveGetRequest) -> PrimitiveGetDTO:
        return super().get(session, request)

    @sqla_session_context()
    def list(self, session: Session, request: PrimitiveListRequest) -> PrimitiveListDTO:
        return super().list(session, request)

    @sqla_session_context()
    def update(self, session: Session, request: PrimitiveUpdateRequest) -> PrimitiveUpdateDTO:
        return super().update(session, request)

    @sqla_session_context()
    def delete(self, session: Session, request: PrimitiveDeleteRequest) -> PrimitiveDeleteDTO:
        return super().delete(session, request)


class PrimitiveTestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository):
        yield
        session = repository.session()
        session.query(PrimitiveSqlaModel).delete()
        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return PrimitiveRepository()
