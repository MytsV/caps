import uuid
from datetime import datetime
from typing import List

from lib.core.error import BaseError
from lib.core.models import TBaseCoreModel
from lib.core.dto import TBaseDTO, SuccessDTO
from lib.infrastructure.secondary_ports import (
    BaseCrudRepositoryOutputPort,
    TBaseCrudRequest,
    TCreateRequest,
    CreatedDTO,
    CreatedData,
    TUpdateRequest,
    UpdatedDTO,
    TDeleteRequest,
    TGetRequest,
    UpdatedData,
    DeletedDTO,
    DeletedData,
)
from lib.infrastructure.repository.sqla.models import SoftSqlaModelBase
from lib.infrastructure.repository.sqla.utils import sqla_session_context

from sqlalchemy.orm import Session


class BaseSqlaCrudRepository(BaseCrudRepositoryOutputPort[Session, TBaseCoreModel]):
    def __init__(self, sqla_model: type[SoftSqlaModelBase]) -> None:
        self._sqla_model = sqla_model

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: TCreateRequest) -> CreatedDTO[TBaseCoreModel] | BaseError:
        try:
            instance = self._sqla_model.from_dict(request.data)
            instance.save(session=session)
            session.commit()
        except Exception as e:
            return BaseError(
                message=f"Error creating a new entity: {str(e)}",
                name="Error creating a new entity",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )

        return CreatedDTO[TBaseCoreModel](
            data=CreatedData[TBaseCoreModel](data=instance.to_core_model(), created_at=datetime.now())
        )

    @sqla_session_context()
    def get(self, session: Session, request: TGetRequest) -> TBaseDTO[TBaseCoreModel]:
        instance = session.query(self._sqla_model).filter_by(id=request.id).first()
        if not instance:
            return BaseError(
                message=f"{self._sqla_model.__name__} not found",
                name="Entity not found",
                errorType="not_found",
                context={},
                digest=str(uuid.uuid4()),
            )

        return SuccessDTO[TBaseCoreModel](data=instance.to_core_model())

    @sqla_session_context()
    def list(self, session: Session, request: TBaseCrudRequest) -> TBaseDTO[List[TBaseCoreModel]]:
        try:
            instances = session.query(self._sqla_model).all()
            return SuccessDTO[List[TBaseCoreModel]](data=[instance.to_core_model() for instance in instances])
        except Exception as e:
            return BaseError(
                message=f"Error listing entities: {str(e)}",
                name="Error listing entities",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )

    @sqla_session_context()
    def update(self, session: Session, request: TUpdateRequest) -> UpdatedDTO[TBaseCoreModel] | BaseError:
        try:
            instance = session.query(self._sqla_model).filter_by(id=request.id).first()
            if not instance:
                return BaseError(
                    message=f"{self._sqla_model.__name__} not found",
                    name="Entity not found",
                    errorType="not_found",
                    context={},
                    digest=str(uuid.uuid4()),
                )

            for key, value in request.data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
                elif value is not None:
                    return BaseError(
                        message=f"Invalid field: {key}",
                        name="Invalid field",
                        errorType="invalid_field",
                        context={},
                        digest=str(uuid.uuid4()),
                    )

            session.commit()
            return UpdatedDTO[TBaseCoreModel](
                data=UpdatedData[TBaseCoreModel](data=instance.to_core_model(), updated_at=datetime.now())
            )
        except Exception as e:
            return BaseError(
                message=f"Error updating entity: {str(e)}",
                name="Error updating entity",
                errorType="ErrorUpdatingEntity",
                context={},
                digest=str(uuid.uuid4()),
            )

    @sqla_session_context()
    def delete(self, session: Session, request: TDeleteRequest) -> DeletedDTO[TBaseCoreModel] | BaseError:
        try:
            instance = session.query(self._sqla_model).filter_by(id=request.id).first()
            if not instance:
                return BaseError(
                    message=f"{self._sqla_model.__name__} not found",
                    name="Entity not found",
                    errorType="not_found",
                    context={},
                    digest=str(uuid.uuid4()),
                )

            session.delete(instance)
            session.commit()

            return DeletedDTO[TBaseCoreModel](
                data=DeletedData[TBaseCoreModel](id=request.id, deleted_at=datetime.now())
            )
        except Exception as e:
            return BaseError(
                message=f"Error deleting entity: {str(e)}",
                name="Error deleting entity",
                errorType="database_error",
                context=e,
                digest="ErrorWhileDeletingEntity",
            )
