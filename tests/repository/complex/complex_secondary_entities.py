import uuid
from typing import List, Optional

from pydantic import BaseModel

from lib.sdk.core.error import BaseError, ErrorType
from lib.sdk.core.request import BaseIdentifiedRequest, BaseListRequest

from lib.sdk.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository, validate_fields
from lib.sdk.core.dto import TBaseDTO, SuccessDTO, TBaseListDTO
from sqlalchemy.orm import Session

from lib.sdk.infrastructure.repository.sqla.utils import sqla_session_context
import pytest

from tests.repository.models import ComplexCoreModel, DepartmentCoreModel, AssignmentCoreModel, StudentCoreModel
from tests.repository.sqla_models import (
    StudentSqlaModel,
    AssignmentSqlaModel,
    SyllabusSqlaModel,
    ComplexSqlaModel,
    DepartmentSqlaModel,
    course_student_association,
)


class SyllabusCreateModel(BaseModel):
    name: str
    content: str


class ComplexCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    department_id: int
    syllabus: SyllabusCreateModel
    source_data_ids: Optional[List[int]] = None


class ComplexGetRequest(BaseIdentifiedRequest):
    pass


class ComplexDeleteRequest(BaseIdentifiedRequest):
    pass


class ComplexUpdateRequest(BaseIdentifiedRequest):
    name: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None
    status: Optional[str] = None
    assignments_ids: Optional[List[int]] = None
    enrolled_students_ids: Optional[List[int]] = None


class ComplexListRequest(BaseListRequest):
    name: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[int] = None


ComplexCreateDTO = TBaseDTO[ComplexCoreModel]
ComplexGetDTO = TBaseDTO[ComplexCoreModel]
ComplexListDTO = TBaseListDTO[List[ComplexCoreModel]]
ComplexUpdateDTO = TBaseDTO[ComplexCoreModel]
ComplexDeleteDTO = TBaseDTO[ComplexCoreModel]


class DepartmentCreateRequest(BaseModel):
    name: str
    code: str


DepartmentCreateDTO = TBaseDTO[DepartmentCoreModel]


class AssignmentCreateRequest(BaseModel):
    name: str
    description: str
    due_date: str
    course_id: int


AssignmentCreateDTO = TBaseDTO[AssignmentCoreModel]


class StudentCreateRequest(BaseModel):
    name: str
    email: str


StudentCreateDTO = TBaseDTO[StudentCoreModel]


class ComplexRepository(DefaultSqlaCrudRepository[ComplexCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=ComplexSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: ComplexCreateRequest) -> ComplexCreateDTO:
        return super().create(session, request)

    @sqla_session_context()
    def update(self, session: Session, request: ComplexUpdateRequest) -> ComplexUpdateDTO:
        return super().update(session, request)

    @sqla_session_context()
    def get(self, session: Session, request: ComplexGetRequest) -> ComplexGetDTO:
        return super().get(session, request)

    @sqla_session_context()
    def list(self, session: Session, request: ComplexListRequest) -> ComplexListDTO:
        return super().list(session, request)

    @sqla_session_context()
    def delete(self, session: Session, request: ComplexDeleteRequest) -> ComplexDeleteDTO:
        return super().delete(session, request)


class DepartmentRepository(DefaultSqlaCrudRepository[DepartmentCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=DepartmentSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: DepartmentCreateRequest) -> DepartmentCreateDTO:
        return super().create(session, request)


class AssignmentRepository(DefaultSqlaCrudRepository[AssignmentCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=AssignmentSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: AssignmentCreateRequest) -> AssignmentCreateDTO:
        return super().create(session, request)


class StudentRepository(DefaultSqlaCrudRepository[StudentCoreModel]):
    def __init__(self) -> None:
        super().__init__(sqla_model=StudentSqlaModel)

    @sqla_session_context()
    def session(self, session: Session) -> Session:
        return session

    @sqla_session_context()
    def create(self, session: Session, request: StudentCreateRequest) -> StudentCreateDTO:
        return super().create(session, request)


class ComplexTestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(self, repository, department_repository, student_repository, assignment_repository):
        yield
        session = repository.session()
        session.execute(course_student_association.delete())

        session.query(SyllabusSqlaModel).delete()
        session.query(AssignmentSqlaModel).delete()
        session.query(ComplexSqlaModel).delete()
        session.query(StudentSqlaModel).delete()
        session.query(DepartmentSqlaModel).delete()

        session.commit()

    @pytest.fixture(scope="class")
    def repository(self):
        return ComplexRepository()

    @pytest.fixture(scope="class")
    def department_repository(self):
        return DepartmentRepository()

    @pytest.fixture(scope="class")
    def student_repository(self):
        return StudentRepository()

    @pytest.fixture(scope="class")
    def assignment_repository(self):
        return AssignmentRepository()

    @pytest.fixture
    def department(self, department_repository):
        request = DepartmentCreateRequest(name="Computer Science", code="CS101")
        result = department_repository.create(request)
        return result.data

    @pytest.fixture
    def student(self, student_repository):
        request = StudentCreateRequest(name="John Doe", email="john@example.com")
        result = student_repository.create(request)
        return result.data

    @pytest.fixture
    def course(self, repository, department):
        request = ComplexCreateRequest(
            name="Introduction to Programming",
            description="Learn basics of programming",
            department_id=department.id,
            syllabus=SyllabusCreateModel(name="Programming Syllabus", content="Week 1: Variables..."),
        )
        result = repository.create(request)
        return result.data

    @pytest.fixture
    def assignment(self, assignment_repository, course):
        request = AssignmentCreateRequest(
            name="First Assignment", description="Create Hello World", due_date="2025-02-01", course_id=course.id
        )
        result = assignment_repository.create(request)
        return result.data
