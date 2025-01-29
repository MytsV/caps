from lib.core.error import exception_handler, ValidationError, DatabaseError, NotFoundError
from lib.core.models import TBaseCoreModel
from lib.core.dto import TBaseDTO, SuccessDTO
from lib.core.request import BaseIdentifiedRequest, BaseListRequest
from lib.infrastructure.secondary_ports.base_crud_secondary_ports import (
    BaseCrudOutputPort
)
from lib.infrastructure.repository.sqla.models import TSoftModelBase

from typing import Generic, List
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
        self._model_name = sqla_model.__tablename__ or sqla_model.__name__

    def session(self, session: Session) -> Session:
        raise NotImplementedError("You must implement the session method. It should return a session object.")

    @exception_handler()
    def create(self, session: Session, request: BaseModel) -> TBaseDTO[TBaseCoreModel]:
        data = request.model_dump()
        try:
            instance = self._sqla_model.from_dict(data)
        except ValueError as e:
            raise ValidationError(
                f"Invalid field in {self._model_name} create request: {str(e)}",
                context={"data": data}
            )

        try:
            instance.save(session=session)
            session.commit()
            return SuccessDTO(data=instance.to_core_model())
        except Exception as e:
            raise DatabaseError(
                f"Error creating {self._model_name}",
                context={"original_error": str(e), "data": data}
            )

    @exception_handler()
    def get(self, session: Session, request: BaseIdentifiedRequest) -> TBaseDTO[TBaseCoreModel]:
        instance = session.query(self._sqla_model).get(request.id)
        if not instance:
            raise NotFoundError(
                f"{self._model_name} with id {request.id} not found",
                context={"id": request.id}
            )

        try:
            return SuccessDTO(data=instance.to_core_model())
        except Exception as e:
            raise DatabaseError(
                f"Error retrieving {self._model_name}",
                context={"original_error": str(e), "id": request.id}
            )

    @exception_handler()
    def list(self, session: Session, request: BaseListRequest) -> TBaseDTO[List[TBaseCoreModel]]:
        if (request.page is not None and request.page <= 0) or (request.page_size is not None and request.page_size <= 0):
            raise ValidationError(
                f"Error listing {self._model_name}: page and page_size must be greater than 0",
                context={"page": request.page, "page_size": request.page_size}
            )

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
            raise DatabaseError(
                f"Error listing {self._model_name}s",
                context={"original_error": str(e), "filters": request.model_dump()}
            )

    @exception_handler()
    def update(self, session: Session, request: BaseIdentifiedRequest) -> TBaseDTO[TBaseCoreModel]:
        instance = session.query(self._sqla_model).get(request.id)
        if not instance:
            raise NotFoundError(
                f"{self._model_name} with id {request.id} not found",
                context={"id": request.id}
            )

        update_data = request.model_dump()
        update_data.pop('id', None)

        is_valid = validate_fields(self._sqla_model, update_data)
        if not is_valid:
            raise ValidationError(
                f"Invalid fields in {self._model_name} update request.",
                context={"update_data": update_data}
            )

        try:
            instance.update(update_data, session=session)
            session.commit()
            return SuccessDTO(data=instance.to_core_model())
        except Exception as e:
            raise DatabaseError(
                f"Error updating {self._model_name}",
                context={"original_error": str(e), "id": request.id, "update_data": update_data}
            )

    @exception_handler()
    def delete(self, session: Session, request: BaseIdentifiedRequest) -> TBaseDTO[TBaseCoreModel]:
        instance = session.query(self._sqla_model).get(request.id)
        if not instance:
            raise NotFoundError(
                f"{self._model_name} with id {request.id} not found",
                context={"id": request.id}
            )

        try:
            core_model = instance.to_core_model()
            session.delete(instance)
            session.commit()
            return SuccessDTO(data=core_model)
        except Exception as e:
            raise DatabaseError(
                f"Error deleting {self._model_name}",
                context={"original_error": str(e), "id": request.id}
            )
