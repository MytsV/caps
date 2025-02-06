from lib.sdk.core.dto import SuccessDTO
from lib.sdk.core.error import BaseError
from tests.repository.complex.complex_secondary_entities import (
    ComplexTestSetup,
    ComplexCreateRequest,
    SyllabusCreateModel,
    ComplexGetRequest,
    ComplexListRequest,
    ComplexUpdateRequest,
    ComplexDeleteRequest,
    ComplexRepository,
    ComplexCreateDTO,
    ComplexGetDTO,
    ComplexListDTO,
    ComplexUpdateDTO,
    ComplexDeleteDTO,
)
from tests.repository.models import DepartmentCoreModel, ComplexCoreModel, StudentCoreModel, AssignmentCoreModel


class TestComplexRepository(ComplexTestSetup):
    def test_create_course(self, repository: ComplexRepository, department: DepartmentCoreModel) -> None:
        request: ComplexCreateRequest = ComplexCreateRequest(
            name="Python Programming",
            description="Advanced Python course",
            department_id=department.id,
            syllabus=SyllabusCreateModel(name="Python Syllabus", content="Week 1: Python Basics"),
        )
        result: ComplexCreateDTO = repository.create(request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Python Programming"
        assert result.data.department.id == department.id
        assert result.data.syllabus.name == "Python Syllabus"

    def test_get_course(self, repository: ComplexRepository, course: ComplexCoreModel) -> None:
        result: ComplexGetDTO = repository.get(ComplexGetRequest(id=course.id))

        assert isinstance(result, SuccessDTO)
        assert result.data.id == course.id
        assert result.data.name == course.name

    def test_list_filter_by_name(self, repository: ComplexRepository, department: DepartmentCoreModel) -> None:
        create_result_1: ComplexCreateDTO = repository.create(
            ComplexCreateRequest(
                name="Target Course",
                department_id=department.id,
                syllabus=SyllabusCreateModel(name="Target Syllabus", content="Content"),
            )
        )
        if isinstance(create_result_1, BaseError):
            raise ValueError("Failed to create first test course")

        create_result_2: ComplexCreateDTO = repository.create(
            ComplexCreateRequest(
                name="Other Course",
                department_id=department.id,
                syllabus=SyllabusCreateModel(name="Other Syllabus", content="Content"),
            )
        )
        if isinstance(create_result_2, BaseError):
            raise ValueError("Failed to create second test course")

        result: ComplexListDTO = repository.list(ComplexListRequest(name="Target Course"))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Target Course"

    def test_update_course(
        self, repository: ComplexRepository, course: ComplexCoreModel, student: StudentCoreModel
    ) -> None:
        request: ComplexUpdateRequest = ComplexUpdateRequest(
            id=course.id, name="Updated Course", enrolled_students_ids=[student.id]
        )
        result: ComplexUpdateDTO = repository.update(request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Updated Course"
        assert len(result.data.enrolled_students) == 1
        assert result.data.enrolled_students[0].id == student.id

    def test_delete_course(self, repository: ComplexRepository, course: ComplexCoreModel) -> None:
        result: ComplexDeleteDTO = repository.delete(ComplexDeleteRequest(id=course.id))

        assert isinstance(result, SuccessDTO)
        assert result.data.id == course.id

        # Verify course is deleted
        get_result: ComplexGetDTO = repository.get(ComplexGetRequest(id=course.id))
        assert not isinstance(get_result, SuccessDTO)

    def test_list_filter_by_department(self, repository: ComplexRepository, department: DepartmentCoreModel) -> None:
        create_result: ComplexCreateDTO = repository.create(
            ComplexCreateRequest(
                name="Department Test Course",
                department_id=department.id,
                syllabus=SyllabusCreateModel(name="Test Syllabus", content="Content"),
            )
        )
        if isinstance(create_result, BaseError):
            raise ValueError("Failed to create test course")

        result: ComplexListDTO = repository.list(ComplexListRequest(department_id=department.id))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) >= 1
        assert all(course.department.id == department.id for course in result.data)

    def test_update_assignments(
        self, repository: ComplexRepository, course: ComplexCoreModel, assignment: AssignmentCoreModel
    ) -> None:
        request: ComplexUpdateRequest = ComplexUpdateRequest(id=course.id, assignments_ids=[assignment.id])
        result: ComplexUpdateDTO = repository.update(request)

        assert isinstance(result, SuccessDTO)
        assert len(result.data.assignments) == 1
        assert result.data.assignments[0].id == assignment.id

    def test_create_invalid_department(self, repository: ComplexRepository) -> None:
        request: ComplexCreateRequest = ComplexCreateRequest(
            name="Invalid Course",
            department_id=99999,  # Non-existent department
            syllabus=SyllabusCreateModel(name="Test Syllabus", content="Content"),
        )
        result: ComplexCreateDTO = repository.create(request)

        assert not isinstance(result, SuccessDTO)
