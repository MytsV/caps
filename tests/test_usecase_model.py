from typing import Any
from lib.core.primary_ports import BaseInputPort, BaseOutputPort
from lib.core.usecase_models import BaseErrorResponseModel, BaseRequestModel, BaseResponseModel
from lib.core.view_model import BaseViewModel


class ResponseModel(BaseResponseModel):
    name: str


class RequestModel(BaseRequestModel):
    name: str
    type: str


class ErrorResponseModel(BaseErrorResponseModel):
    error: str


class ViewModel(BaseViewModel):
    name: str


class UseCase(BaseInputPort[RequestModel, ResponseModel, ErrorResponseModel]):

    def execute(self, requestModel: RequestModel) -> ResponseModel | ErrorResponseModel:
        self.logger.info(f"Executing {self} with {requestModel}")
        return ResponseModel(name=requestModel.name)


class Presenter(BaseOutputPort[ResponseModel, ErrorResponseModel, ViewModel]):
    def __init__(self) -> None:
        super().__init__()

    def present_success(self, responseModel: ResponseModel) -> ViewModel:
        return ViewModel(status=True, code=200, name=responseModel.name)

    def present_error(self, errorModel: ErrorResponseModel) -> ViewModel:
        return ViewModel(
            name="Test Error",
            status=False,
            code=errorModel.code,
            errorCode=500,
            errorMessage=errorModel.error,
            errorName=errorModel.error,
            errorType="Error",
        )


def test_usecase_models() -> None:

    usecase: BaseInputPort[RequestModel, ResponseModel, ErrorResponseModel] = UseCase()
    requestModel = RequestModel(name="Test", type="Test")
    response = usecase.execute(requestModel=requestModel)

    assert isinstance(response, ResponseModel)
    assert response.name == "Test"
    assert response.status == True

    presenter = Presenter()

    view_model = presenter.present_success(response)
    assert view_model.status == True
    assert view_model.code == 200
    assert view_model.name == "Test"


def test_usecase_models_error_case() -> None:

    usecase: BaseInputPort[RequestModel, ResponseModel, ErrorResponseModel] = UseCase()
    requestModel = RequestModel(name="Test", type="Test")
    response = usecase.execute(requestModel=requestModel)

    assert isinstance(response, ResponseModel)
    assert response.name == "Test"
    assert response.status == True

    presenter = Presenter()

    view_model = presenter.present_error(ErrorResponseModel(error="Error", code=500, message="Error"))
    assert view_model.status == False
    assert view_model.code == 500
    assert view_model.errorCode == 500
    assert view_model.name == "Test Error"
