from typing import Any
from lib.core.primary_ports import BaseInputPort, BaseOutputPort
from lib.core.usecase_models import BaseErrorResponseModel, BaseRequestModel, BaseResponseModel


class ResponseModel(BaseResponseModel):
    name: str


class RequestModel(BaseRequestModel):
    name: str
    type: str


class ErrorResponseModel(BaseErrorResponseModel):
    error: str


class UseCase(BaseInputPort[RequestModel]):
    def __init__(self, presenter: BaseOutputPort[ResponseModel, ErrorResponseModel]) -> None:
        super().__init__()
        self.presenter = presenter

    def execute(self, requestModel: RequestModel) -> None:
        self.logger.info(f"Executing {self} with {requestModel}")
        responseModel = ResponseModel(name=requestModel.name)
        self.logger.info(f"Returning {responseModel}")
        self.presenter.presentSuccess(responseModel)


class Presenter(BaseOutputPort[ResponseModel, ErrorResponseModel]):
    def __init__(self) -> None:
        super().__init__()

    def presentSuccess(self, responseModel: ResponseModel) -> None:
        print(f"Success: {responseModel}")

    def presentError(self, errorModel: ErrorResponseModel) -> None:
        print(f"Error: {errorModel}")


def test_usecase_models(caplog: Any, capfd: Any) -> None:
    usecase: BaseInputPort[RequestModel] = UseCase(presenter=Presenter())
    requestModel = RequestModel(name="Test", type="Test")
    usecase.execute(requestModel=requestModel)
    # capture log output
    out, err = capfd.readouterr()
    assert out == "Success: status=True name='Test'\n"
