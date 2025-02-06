from typing import List, Optional, Generator

from pydantic import BaseModel

from lib.sdk.core.error import BaseError
from lib.sdk.core.request import BaseIdentifiedRequest, BaseListRequest
from lib.sdk.infrastructure.repository.sqla.database import Database

from lib.sdk.infrastructure.repository.sqla.default_sqla_crud_repository import DefaultSqlaCrudRepository
from lib.sdk.core.dto import TBaseDTO, TBaseListDTO

from lib.sdk.infrastructure.repository.sqla.utils import sqla_database_context
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


# Request Types for Department
class DepartmentCreateRequest(BaseModel):
    name: str
    code: str
    status: str = "active"


class DepartmentGetRequest(BaseIdentifiedRequest):
    pass


class DepartmentDeleteRequest(BaseIdentifiedRequest):
    pass


class DepartmentUpdateRequest(BaseIdentifiedRequest):
    name: str | None = None
    code: str | None = None
    status: str | None = None


class DepartmentListRequest(BaseListRequest):
    name: str | None = None
    code: str | None = None
    status: str | None = None


# DTO Types for Department
DepartmentCreateDTO = TBaseDTO[DepartmentCoreModel]
DepartmentGetDTO = TBaseDTO[DepartmentCoreModel]
DepartmentListDTO = TBaseListDTO[List[DepartmentCoreModel]]
DepartmentUpdateDTO = TBaseDTO[DepartmentCoreModel]
DepartmentDeleteDTO = TBaseDTO[DepartmentCoreModel]


# Request Types for Assignment
class AssignmentCreateRequest(BaseModel):
    name: str
    description: str
    due_date: str
    course_id: int
    status: str = "active"


class AssignmentGetRequest(BaseIdentifiedRequest):
    pass


class AssignmentDeleteRequest(BaseIdentifiedRequest):
    pass


class AssignmentUpdateRequest(BaseIdentifiedRequest):
    name: str | None = None
    description: str | None = None
    due_date: str | None = None
    course_id: int | None = None
    status: str | None = None


class AssignmentListRequest(BaseListRequest):
    name: str | None = None
    course_id: int | None = None
    status: str | None = None


# DTO Types for Assignment
AssignmentCreateDTO = TBaseDTO[AssignmentCoreModel]
AssignmentGetDTO = TBaseDTO[AssignmentCoreModel]
AssignmentListDTO = TBaseListDTO[List[AssignmentCoreModel]]
AssignmentUpdateDTO = TBaseDTO[AssignmentCoreModel]
AssignmentDeleteDTO = TBaseDTO[AssignmentCoreModel]


# Request Types for Student
class StudentCreateRequest(BaseModel):
    name: str
    email: str
    status: str = "active"


class StudentGetRequest(BaseIdentifiedRequest):
    pass


class StudentDeleteRequest(BaseIdentifiedRequest):
    pass


class StudentUpdateRequest(BaseIdentifiedRequest):
    name: str | None = None
    email: str | None = None
    status: str | None = None


class StudentListRequest(BaseListRequest):
    name: str | None = None
    email: str | None = None
    status: str | None = None


# DTO Types for Student
StudentCreateDTO = TBaseDTO[StudentCoreModel]
StudentGetDTO = TBaseDTO[StudentCoreModel]
StudentListDTO = TBaseListDTO[List[StudentCoreModel]]
StudentUpdateDTO = TBaseDTO[StudentCoreModel]
StudentDeleteDTO = TBaseDTO[StudentCoreModel]


# Repository Implementations
class ComplexRepository(
    DefaultSqlaCrudRepository[
        ComplexCoreModel,
        ComplexCreateRequest,
        ComplexGetRequest,
        ComplexListRequest,
        ComplexUpdateRequest,
        ComplexDeleteRequest,
    ]
):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=ComplexSqlaModel, database=database)

    def create(self, request: ComplexCreateRequest) -> ComplexCreateDTO:
        return super().create(request)

    def get(self, request: ComplexGetRequest) -> ComplexGetDTO:
        return super().get(request)

    def list(self, request: ComplexListRequest) -> ComplexListDTO:
        return super().list(request)

    def update(self, request: ComplexUpdateRequest) -> ComplexUpdateDTO:
        return super().update(request)

    def delete(self, request: ComplexDeleteRequest) -> ComplexDeleteDTO:
        return super().delete(request)


class DepartmentRepository(
    DefaultSqlaCrudRepository[
        DepartmentCoreModel,
        DepartmentCreateRequest,
        DepartmentGetRequest,
        DepartmentListRequest,
        DepartmentUpdateRequest,
        DepartmentDeleteRequest,
    ]
):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=DepartmentSqlaModel, database=database)

    def create(self, request: DepartmentCreateRequest) -> DepartmentCreateDTO:
        return super().create(request)

    def get(self, request: DepartmentGetRequest) -> DepartmentGetDTO:
        return super().get(request)

    def list(self, request: DepartmentListRequest) -> DepartmentListDTO:
        return super().list(request)

    def update(self, request: DepartmentUpdateRequest) -> DepartmentUpdateDTO:
        return super().update(request)

    def delete(self, request: DepartmentDeleteRequest) -> DepartmentDeleteDTO:
        return super().delete(request)


class AssignmentRepository(
    DefaultSqlaCrudRepository[
        AssignmentCoreModel,
        AssignmentCreateRequest,
        AssignmentGetRequest,
        AssignmentListRequest,
        AssignmentUpdateRequest,
        AssignmentDeleteRequest,
    ]
):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=AssignmentSqlaModel, database=database)

    def create(self, request: AssignmentCreateRequest) -> AssignmentCreateDTO:
        return super().create(request)

    def get(self, request: AssignmentGetRequest) -> AssignmentGetDTO:
        return super().get(request)

    def list(self, request: AssignmentListRequest) -> AssignmentListDTO:
        return super().list(request)

    def update(self, request: AssignmentUpdateRequest) -> AssignmentUpdateDTO:
        return super().update(request)

    def delete(self, request: AssignmentDeleteRequest) -> AssignmentDeleteDTO:
        return super().delete(request)


class StudentRepository(
    DefaultSqlaCrudRepository[
        StudentCoreModel,
        StudentCreateRequest,
        StudentGetRequest,
        StudentListRequest,
        StudentUpdateRequest,
        StudentDeleteRequest,
    ]
):
    @sqla_database_context()
    def __init__(self, database: Database | None = None) -> None:
        if database is None:
            raise ValueError("Database has not been injected")
        super().__init__(sqla_model=StudentSqlaModel, database=database)

    def create(self, request: StudentCreateRequest) -> StudentCreateDTO:
        return super().create(request)

    def get(self, request: StudentGetRequest) -> StudentGetDTO:
        return super().get(request)

    def list(self, request: StudentListRequest) -> StudentListDTO:
        return super().list(request)

    def update(self, request: StudentUpdateRequest) -> StudentUpdateDTO:
        return super().update(request)

    def delete(self, request: StudentDeleteRequest) -> StudentDeleteDTO:
        return super().delete(request)


class ComplexTestSetup:
    @pytest.fixture(autouse=True)
    def cleanup(
        self,
        repository: ComplexRepository,
        department_repository: DepartmentRepository,
        student_repository: StudentRepository,
        assignment_repository: AssignmentRepository,
    ) -> Generator[None, None, None]:
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
    def repository(self) -> ComplexRepository:
        return ComplexRepository()

    @pytest.fixture(scope="class")
    def department_repository(self) -> DepartmentRepository:
        return DepartmentRepository()

    @pytest.fixture(scope="class")
    def student_repository(self) -> StudentRepository:
        return StudentRepository()

    @pytest.fixture(scope="class")
    def assignment_repository(self) -> AssignmentRepository:
        return AssignmentRepository()

    @pytest.fixture
    def department(self, department_repository: DepartmentRepository) -> DepartmentCoreModel:
        request = DepartmentCreateRequest(name="Computer Science", code="CS101")
        result = department_repository.create(request)
        if isinstance(result, BaseError):
            raise ValueError("Error creating department")
        return result.data

    @pytest.fixture
    def student(self, student_repository: StudentRepository) -> StudentCoreModel:
        request = StudentCreateRequest(name="John Doe", email="john@example.com")
        result = student_repository.create(request)
        if isinstance(result, BaseError):
            raise ValueError("Error creating student")
        return result.data

    @pytest.fixture
    def course(self, repository: ComplexRepository, department: DepartmentCoreModel) -> ComplexCoreModel:
        request = ComplexCreateRequest(
            name="Introduction to Programming",
            description="Learn basics of programming",
            department_id=department.id,
            syllabus=SyllabusCreateModel(name="Programming Syllabus", content="Week 1: Variables..."),
        )
        result = repository.create(request)
        if isinstance(result, BaseError):
            raise ValueError("Error creating course")
        return result.data

    @pytest.fixture
    def assignment(self, assignment_repository: AssignmentRepository, course: ComplexCoreModel) -> AssignmentCoreModel:
        request = AssignmentCreateRequest(
            name="First Assignment", description="Create Hello World", due_date="2025-02-01", course_id=course.id
        )
        result = assignment_repository.create(request)
        if isinstance(result, BaseError):
            raise ValueError("Error creating assignment")
        return result.data
