"""
Tests for type hinting

Pass 'debug' as the first argument to this script see the mypy --strict errors for the whole file
so you can check that the tests are capturing the errors that involve them
Have in mind that not all tests use the --strict flag
"""

from abc import abstractmethod
import sys
from typing import Generic, TypeVar
from lib.core.bac import BaseAbstractClass
from lib.core.primary_ports import BaseInputPort, BaseOutputPort
from lib.core.usecase_models import BaseErrorResponseModel, BaseRequestModel, BaseResponseModel

from lib.core.view_model import BaseViewModel
from tests.types.mypytest_prototype import debug_mypy, object_mypy_error_report


if len(sys.argv) > 1:
    if sys.argv[1].lower() == "debug":
        debug_mypy(__file__)


class ResponseModel(BaseResponseModel):
    name: str


class ErrorResponseModel(BaseErrorResponseModel):
    name: str


class RequestModel(BaseRequestModel):
    name: str
    type: str


class ViewModel(BaseViewModel):
    pass


def test_subtypes() -> None:
    """
    Directly from mypy 1.5.1 docs:
    https://mypy.readthedocs.io/en/stable/kinds_of_types.html#the-type-of-class-objects
    """

    class User:
        # Defines fields like name, email
        pass

    class BasicUser(User):
        def upgrade(self) -> None:
            """Upgrade to Pro"""

    class ProUser(User):
        def pay(self) -> None:
            """Pay bill"""

    U = TypeVar("U", bound=User)

    def new_user(user_class: type[U]) -> U:
        user = user_class()
        # (Here we could write the user object to a database)
        return user

    mypy_test_error_report = object_mypy_error_report(new_user, __file__)

    # assert that the class is not in the mypy error report
    assert len(mypy_test_error_report) == 0

    beginner = new_user(BasicUser)  # Inferred type by the IDE is BasicUser
    beginner.upgrade()  # OK for the IDE


def test_badly_typed_subtype_intuition() -> None:
    """
    This will very clearly fail, as we have not type hinted appropriatedly
    """

    class BadlyTypedUseCase(BaseInputPort):
        def __init__(self, presenter: BaseOutputPort) -> None:
            super().__init__()
            self.presenter = presenter

        # mypy should capture that RequestModel is not BaseRequestModel, when written like this
        def execute(self, requestModel: RequestModel) -> None:
            pass

    mypy_test_error_report = object_mypy_error_report(BadlyTypedUseCase, __file__)

    # assert that the class is in the mypy error report
    assert len(mypy_test_error_report) != 0
    # assert how many intentional type errors you coded
    # We're not pasing type-args to BaseInputPort and BaseOutputPort, so we get 2 errors
    assert len(mypy_test_error_report) == 2


def test_badly_typed_type_and_subtype() -> None:
    """
    However, straightfowardly applying the docs to our example, we DON'T get a pass from mypy
    see: https://mypy.readthedocs.io/en/stable/kinds_of_types.html#the-type-of-class-objects
    """

    TRequestModel = TypeVar("TRequestModel", bound=BaseRequestModel)

    class BaseInputPort_MypyDocs(BaseAbstractClass):
        def __init__(self) -> None:
            super().__init__()

        @abstractmethod
        def execute(self, requestModel: type[TRequestModel]) -> None:
            pass

    class UseCase(BaseInputPort_MypyDocs):
        def __init__(self, presenter: BaseOutputPort) -> None:
            super().__init__()
            self.presenter = presenter

        # from the docs, it looks like mypy should capture that RequestModel IS BaseRequestModel,
        # when written like this...
        def execute(self, requestModel: RequestModel) -> None:
            pass

    mypy_test_error_report_1 = object_mypy_error_report(BaseInputPort_MypyDocs, __file__)
    # The BaseInputPort_MypyDocs works fine...
    assert len(mypy_test_error_report_1) == 0

    mypy_test_error_report_2 = object_mypy_error_report(UseCase, __file__)
    # ...but UseCase doesn't!
    assert len(mypy_test_error_report_2) != 0
    # We get the same type-arg missing error for BaseOutputPort
    # And now we also get a mypy error at def execute...
    assert len(mypy_test_error_report_2) == 2


def test_badly_typed_type_and_subtype_with_generic() -> None:
    """
    Generic alone doesn't solve the problem either
    """

    TRequestModel = TypeVar("TRequestModel", bound=BaseRequestModel)

    class BaseInputPort_Generic(BaseAbstractClass, Generic[TRequestModel]):
        def __init__(self) -> None:
            super().__init__()

        @abstractmethod
        def execute(self, requestModel: TRequestModel) -> None:
            pass

    class UseCase(BaseInputPort_Generic):
        def __init__(self, presenter: BaseOutputPort):
            super().__init__()
            self.presenter = presenter

        def execute(self, requestModel: RequestModel) -> None:
            pass

    class UseCase_bad_1(BaseInputPort_Generic):
        def __init__(self, presenter: BaseOutputPort):
            super().__init__()
            self.presenter = presenter

        def execute(self, requestModel: int) -> None:
            pass

    # Everything seems to work...
    mypy_test_error_report_1 = object_mypy_error_report(BaseInputPort_Generic, __file__)

    # NOTE: these tests have to be run without the strict flag
    # to illustrate what mypy without the flag doesn't catch
    # we've configured the project for mypy to be strict and it cannot be overriden

    # mypy_test_error_report_2 = object_mypy_error_report(UseCase, __file__, strict=False)
    # assert len(mypy_test_error_report_1) == 0
    # assert len(mypy_test_error_report_2) == 0

    ## ...but it does because mypy is not checking the corresponding error
    # mypy_test_error_report_3 = object_mypy_error_report(UseCase_bad_1, __file__)
    # assert len(mypy_test_error_report_3) == 0

    # This illustrates that need the strict flag to catch the type-arg missing error, not passed to BaseInputPort_Generic and BaseOutputPort
    mypy_test_error_report_3_strict = object_mypy_error_report(UseCase_bad_1, __file__, strict=True)
    assert len(mypy_test_error_report_3_strict) == 2


def test_correctly_typed_type_and_subtype() -> None:
    """
    Mypy with the --strict flag, using bounds, TypeVar, and Generic, works as expected
    NOTE: --strict is very picky, and everything must be typed, including the __init__ methods
    and the base classes of the imports as well, see bac.py

    For the combination of bounds, TypeVar, NewVar, and Generic, see the second answer here:
    https://stackoverflow.com/questions/54346721/mypy-argument-of-method-incompatible-with-supertype
    """

    # This is the way to tell mypy to accept a type and any subtypes
    BoundedBaseRequestModel = TypeVar("BoundedBaseRequestModel", bound=BaseRequestModel)

    BoundedBaseResponseModel = TypeVar("BoundedBaseResponseModel", bound=BaseResponseModel)

    BoundedBaseErrorResponseModel = TypeVar("BoundedBaseErrorResponseModel", bound=BaseErrorResponseModel)

    class BaseInputPort_Generic(
        BaseAbstractClass, Generic[BoundedBaseRequestModel, BoundedBaseResponseModel, BoundedBaseErrorResponseModel]
    ):
        def __init__(self) -> None:
            super().__init__()

        @abstractmethod
        def execute(self, requestModel: BoundedBaseRequestModel) -> None:
            pass

    class UseCase_Passing_Type_To_Generic(BaseInputPort_Generic[RequestModel, ResponseModel, ErrorResponseModel]):
        # NOTE: we NEED to pass the type to the Generic, otherwise mypy --strict will complain
        # that a type is not passed to the Generic
        def __init__(self, presenter: BaseOutputPort[ResponseModel, ErrorResponseModel, ViewModel]) -> None:
            super().__init__()
            self.presenter = presenter

        def execute(self, requestModel: RequestModel) -> None:
            pass

    class UseCase_bad_1(BaseInputPort_Generic):
        # NOTE: watch out for this case!
        # if mypy doesn't have the --strict flag, it will not catch this, see below
        def __init__(self, presenter: BaseOutputPort[ResponseModel, ErrorResponseModel, ViewModel]) -> None:
            super().__init__()
            self.presenter = presenter

        def execute(self, requestModel: int) -> ResponseModel | ErrorResponseModel:
            pass

    class UseCase_bad_2(BaseInputPort_Generic[int, int, int]):
        # If we pass the incorrect type to the Generic, mypy always complains, strict or not
        def __init__(self, presenter: BaseOutputPort[ResponseModel, ErrorResponseModel, ViewModel]) -> None:
            super().__init__()
            self.presenter = presenter

        def execute(self, requestModel: int) -> ResponseModel | ErrorResponseModel:
            pass

    mypy_test_error_report_1 = object_mypy_error_report(BaseInputPort_Generic, __file__, strict=True)
    # The BaseInputPort_MypyDocs works fine, strict or not
    assert len(mypy_test_error_report_1) == 0

    mypy_test_error_report_2 = object_mypy_error_report(UseCase_Passing_Type_To_Generic, __file__, strict=True)
    # This is what we want! passes strict or not
    assert len(mypy_test_error_report_2) == 0

    # mypy_test_error_report_3 = object_mypy_error_report(UseCase_bad_1, __file__)
    ## NOTE: BUT this case is unsafe without --strict!!!
    # assert len(mypy_test_error_report_3) == 0

    mypy_test_error_report_3_strict = object_mypy_error_report(UseCase_bad_1, __file__, strict=True)
    # We need to use the strict flag, otherwise mypy doesn't catch this
    # It's a 'type-arg' missing error, that is only caught with the strict flag
    assert len(mypy_test_error_report_3_strict) == 3

    mypy_test_error_report_4 = object_mypy_error_report(UseCase_bad_2, __file__)
    mypy_test_error_report_4_strict = object_mypy_error_report(UseCase_bad_2, __file__, strict=True)
    # mypy correctly captures this case, strict or not
    assert len(mypy_test_error_report_4) == 5
    assert len(mypy_test_error_report_4_strict) == 5
