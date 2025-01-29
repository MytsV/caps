from lib.core.error import exception_handler, ValidationError, DatabaseError, NotFoundError
from lib.core.models import TBaseCoreModel
from lib.core.dto import TBaseDTO, SuccessDTO, TBaseListDTO, SuccessListDTO
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


def extract_request_data(sqla_model, request_data):
    entity_data = {}
    relationship_data = {}

    for column in sqla_model.__mapper__.columns:
        key = column.key
        if key in request_data:
            entity_data[key] = request_data[key]

    for name, relationship in sqla_model.__mapper__.relationships.items():
        single_id_name = f"{name}_id"
        multiple_ids_name = f"{name}_ids"

        if name in request_data:
            relationship_data[name] = request_data[name]
        elif single_id_name in request_data:
            relationship_data[single_id_name] = request_data[single_id_name]
        elif multiple_ids_name in request_data:
            relationship_data[multiple_ids_name] = request_data[multiple_ids_name]

    return entity_data, relationship_data


def handle_relationships(instance, relationship_data, session):
    for request_field, data in relationship_data.items():
        # Find relationship name by removing _id(s) suffix if present
        relationship_name = request_field.replace('_ids', '').replace('_id', '')
        relationship = instance.__mapper__.relationships[relationship_name]

        # Determine if it's an ID-based update
        is_single_id = request_field.endswith('_id')
        is_multiple_ids = request_field.endswith('_ids')

        # Handle many-to-many or one-to-many relationships
        if relationship.secondary is not None or relationship.uselist:
            if is_multiple_ids:
                related_model = relationship.mapper.class_
                related_instances = session.query(related_model).filter(
                    related_model.id.in_(data)
                ).all()
            else:  # entity data
                related_instances = [relationship.mapper.class_(**entity) for entity in data]

            setattr(instance, relationship_name, related_instances)

        # Handle one-to-one or many-to-one relationships
        else:
            if is_single_id:
                related_model = relationship.mapper.class_
                related_instance = session.query(related_model).get(data)
            else:  # entity data
                related_instance = relationship.mapper.class_(**data)

            setattr(instance, relationship_name, related_instance)


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
        entity_data, relationship_data = extract_request_data(self._sqla_model, data)

        try:
            instance = self._sqla_model.from_dict(entity_data)
            instance.save(session=session)

            if relationship_data:
                handle_relationships(instance, relationship_data, session)

            session.commit()
            return SuccessDTO(data=instance.to_core_model())

        except ValueError as e:
            raise ValidationError(
                f"Invalid field in {self._model_name} create request: {str(e)}",
                context={"data": data}
            )
        except Exception as e:
            session.rollback()
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
    def list(self, session: Session, request: BaseListRequest) -> TBaseListDTO[List[TBaseCoreModel]]:
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

            has_next_page = None

            if request.page is not None:
                page_size = request.page_size or DEFAULT_PAGE_SIZE
                offset = (request.page - 1) * page_size

                # Fetch one extra record to determine if there's a next page
                query = query.offset(offset).limit(page_size + 1)
                results = query.all()

                has_next_page = len(results) > page_size
                instances = results[:page_size]
            else:
                instances = query.all()

            return SuccessListDTO(
                has_next_page=has_next_page,
                data=[instance.to_core_model() for instance in instances]
            )

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

        data = request.model_dump(exclude_none=True)
        data.pop('id', None)

        entity_data, relationship_data = extract_request_data(self._sqla_model, data)

        is_valid = validate_fields(self._sqla_model, entity_data)
        if not is_valid:
            raise ValidationError(
                f"Invalid fields in {self._model_name} update request.",
                context={"update_data": entity_data}
            )

        try:
            # Update regular fields
            instance.update(entity_data, session=session)

            # Handle relationships if any exist
            if relationship_data:
                handle_relationships(instance, relationship_data, session)

            session.commit()
            return SuccessDTO(data=instance.to_core_model())
        except Exception as e:
            session.rollback()
            raise DatabaseError(
                f"Error updating {self._model_name}",
                context={"original_error": str(e), "id": request.id, "data": data}
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
