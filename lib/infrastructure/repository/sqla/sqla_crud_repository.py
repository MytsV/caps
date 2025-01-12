from datetime import datetime
from typing import TypeVar, List

from lib.core.error import BaseError
from lib.core.models import TBaseSDKModel, TEntitySDKModel
from lib.core.dto import TBaseDTO, SuccessDTO
from lib.core.secondary_ports import (
    BaseCrudRepositoryOutputPort,
    TBaseCrudRequest,
    TCreateRequest,
    CreatedDTO,
    CreatedData,
    TUpdateRequest,
    UpdatedDTO,
    TDeleteRequest,
)
from lib.infrastructure.repository.sqla.models import SoftModelBase
from lib.infrastructure.repository.sqla.utils import sqla_session_context

from sqlalchemy.orm import Session


class BaseSqlaCrudRepository(BaseCrudRepositoryOutputPort[Session, TEntitySDKModel]):
    def __init__(self, sqla_model: type[SoftModelBase]) -> None:
        self._sqla_model = sqla_model
        pass

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: TCreateRequest) -> CreatedDTO[TEntitySDKModel] | BaseError:
        try:
            instance = self._sqla_model.from_dict(request.data.dict())
            instance.save(session=session)
            session.commit()
        except Exception as e:
            return BaseError(
                message=f"Error creating a new entity: {str(e)}",
                name="Error creating a new entity",
                errorType="ErrorCreatingNewEntity",
                context=e,
                digest="ErrorWhileCreatingNewEntity",
            )

        return CreatedDTO[TEntitySDKModel](
            data=CreatedData[TEntitySDKModel](data=instance.to_sdk_model(), created_at=datetime.now())
        )

    @sqla_session_context()
    def get(self, session: Session, request: TBaseCrudRequest) -> TBaseDTO[TEntitySDKModel]:
        pass
        # instance = session.query(self._sqla_model).filter_by(id=request.id).first()
        # if not instance:
        #     return BaseError(message=f"{self._sqla_model.__name__} not found")
        #
        # return SuccessDTO[TEntitySDKModel](data=instance.to_sdk_model())

    def list(self, session: Session, request: TBaseCrudRequest) -> TBaseDTO[List[TEntitySDKModel]]:
        raise NotImplementedError(
            "You must implement the list method in your repository. Should 'read' multiple records."
        )

    def update(self, session: Session, request: TUpdateRequest) -> UpdatedDTO[TEntitySDKModel] | BaseError:
        raise NotImplementedError("You must implement the update method in your repository")

    def delete(self, session: Session, request: TDeleteRequest) -> CreatedDTO[TEntitySDKModel] | BaseError:
        raise NotImplementedError("You must implement the delete method in your repository")
