from lib.core.error import BaseError
from lib.core.models import TBaseCoreModel
from lib.core.dto import TBaseDTO, SuccessDTO
from lib.core.request import BaseIdentifiedRequest, BaseListRequest
from lib.infrastructure.secondary_ports.base_crud_secondary_ports import (
    BaseCrudOutputPort
)
from lib.infrastructure.repository.sqla.models import TSoftModelBase

from typing import Generic, List
import uuid
from sqlalchemy.orm import Session
from pydantic import BaseModel

DEFAULT_PAGE_SIZE = 10


def validate_fields(model_class, update_data: dict) -> bool:
    for field, value in update_data.items():
        if not hasattr(model_class, field):
            return False
    return True


class DefaultSqlaCrudRepository(BaseCrudOutputPort[Session], Generic[TBaseCoreModel]):
    def __init__(self, sqla_model: TSoftModelBase) -> None:
        super().__init__()
        self._sqla_model = sqla_model

    def session(self, session: Session) -> Session:
        raise NotImplementedError("You must implement the session method. It should return a session object.")

    def create(self, session: Session, request: BaseModel) -> TBaseDTO[TBaseCoreModel]:
        try:
            data = request.model_dump()
            instance = self._sqla_model.from_dict(data)
            instance.save(session=session)
            session.commit()
            return SuccessDTO(data=instance.to_core_model())

        except ValueError as e:
            return BaseError(
                message=f"Invalid field in create request: {str(e)}",
                name="Invalid field error",
                errorType="validation_error",
                context=e,
                digest=str(uuid.uuid4()),
            )
        except Exception as e:
            return BaseError(
                message=f"Error creating entity: {str(e)}",
                name="Error creating entity",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )

    def get(self, session: Session, request: BaseIdentifiedRequest) -> TBaseDTO[TBaseCoreModel]:
        try:
            instance = session.query(self._sqla_model).get(request.id)
            if not instance:
                return BaseError(
                    message=f"Entity with id {request.id} not found",
                    name="Entity not found",
                    errorType="not_found_error",
                    context={"id": request.id},
                    digest=str(uuid.uuid4()),
                )

            return SuccessDTO(data=instance.to_core_model())

        except Exception as e:
            return BaseError(
                message=f"Error retrieving entity: {str(e)}",
                name="Error retrieving entity",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )

    def list(self, session: Session, request: BaseListRequest) -> TBaseDTO[List[TBaseCoreModel]]:
        try:
            query = session.query(self._sqla_model)

            for field, value in request.model_dump().items():
                if field not in ['page', 'page_size'] and value is not None:
                    query = query.filter(getattr(self._sqla_model, field) == value)

            if request.page is not None:
                page_size = request.page_size or DEFAULT_PAGE_SIZE
                query = query.offset((request.page - 1) * page_size).limit(page_size)

            instances = query.all()
            return SuccessDTO(data=[instance.to_core_model() for instance in instances])

        except Exception as e:
            return BaseError(
                message=f"Error listing entities: {str(e)}",
                name="Error listing entities",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )

    def update(self, session: Session, request: BaseIdentifiedRequest) -> TBaseDTO[TBaseCoreModel]:
        try:
            instance = session.query(self._sqla_model).get(request.id)
            if not instance:
                return BaseError(
                    message=f"Entity with id {request.id} not found",
                    name="Entity not found",
                    errorType="not_found_error",
                    context={"id": request.id},
                    digest=str(uuid.uuid4()),
                )

            update_data = request.model_dump()
            update_data.pop('id', None)

            is_valid = validate_fields(self._sqla_model, update_data)
            if not is_valid:
                raise ValueError()

            instance.update(update_data, session=session)
            session.commit()
            return SuccessDTO(data=instance.to_core_model())
        except ValueError as e:
            return BaseError(
                message=f"Invalid fields in update request: {str(e)}",
                name="Invalid field error",
                errorType="validation_error",
                context=e,
                digest=str(uuid.uuid4()),
            )
        except Exception as e:
            return BaseError(
                message=f"Error updating entity: {str(e)}",
                name="Error updating entity",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )

    def delete(self, session: Session, request: BaseIdentifiedRequest) -> TBaseDTO[TBaseCoreModel]:
        try:
            instance = session.query(self._sqla_model).get(request.id)
            if not instance:
                return BaseError(
                    message=f"Entity with id {request.id} not found",
                    name="Entity not found",
                    errorType="not_found_error",
                    context={"id": request.id},
                    digest=str(uuid.uuid4()),
                )

            session.delete(instance)
            session.commit()

            return SuccessDTO(data=instance.to_core_model())

        except Exception as e:
            return BaseError(
                message=f"Error deleting entity: {str(e)}",
                name="Error deleting entity",
                errorType="database_error",
                context=e,
                digest=str(uuid.uuid4()),
            )
