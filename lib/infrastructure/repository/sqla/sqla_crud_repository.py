from lib.core.models import TBaseSDKModel
from lib.core.dto import TBaseDTO
from lib.core.secontary_ports import BaseCRUDRepositoryOutputPort, TBaseCRUDDTORequestModel
from lib.infrastructure.repository.sqla.models import SoftModelBase
from lib.infrastructure.repository.sqla.utils import sqla_session_context

from sqlalchemy.orm import Session

class BaseSQLACRUDRepository(BaseCRUDRepositoryOutputPort[Session, TBaseSDKModel] ):

    def __init__(self, sqla_model: SoftModelBase) -> None:
        self._sqla_model = sqla_model
        pass
    
    @sqla_session_context()
    def create(self, session: Session, request: TBaseCRUDDTORequestModel) -> TBaseDTO[TBaseSDKModel]:
       pass
       # Something like
       # sqla_instance = request.model(**request.creation_data) 