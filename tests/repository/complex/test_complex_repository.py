from lib.core.dto import SuccessDTO
from tests.repository.complex.complex_secondary_entities import ComplexTestSetup, ComplexCreateRequest, \
    SyllabusCreateModel, ComplexGetRequest, ComplexListRequest, ComplexUpdateRequest, ComplexDeleteRequest


class TestComplexRepository(ComplexTestSetup):
    def test_create_course(self, repository, department):
        request = ComplexCreateRequest(
            name="Python Programming",
            description="Advanced Python course",
            department_id=department.id,
            syllabus=SyllabusCreateModel(
                name="Python Syllabus",
                content="Week 1: Python Basics"
            )
        )
        result = repository.create(request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Python Programming"
        assert result.data.department.id == department.id
        assert result.data.syllabus.name == "Python Syllabus"

    def test_get_course(self, repository, course):
        result = repository.get(ComplexGetRequest(id=course.id))

        assert isinstance(result, SuccessDTO)
        assert result.data.id == course.id
        assert result.data.name == course.name

    def test_list_filter_by_name(self, repository, department):
        create_result_1 = repository.create(ComplexCreateRequest(
            name="Target Course",
            department_id=department.id,
            syllabus=SyllabusCreateModel(
                name="Target Syllabus",
                content="Content"
            )
        ))
        assert isinstance(create_result_1, SuccessDTO)

        create_result_2 = repository.create(ComplexCreateRequest(
            name="Other Course",
            department_id=department.id,
            syllabus=SyllabusCreateModel(
                name="Other Syllabus",
                content="Content"
            )
        ))
        assert isinstance(create_result_2, SuccessDTO)

        result = repository.list(ComplexListRequest(name="Target Course"))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Target Course"

    def test_update_course(self, repository, course, student):
        request = ComplexUpdateRequest(
            id=course.id,
            name="Updated Course",
            student_ids=[student.id]
        )
        result = repository.update(request)

        assert isinstance(result, SuccessDTO)
        assert result.data.name == "Updated Course"
        assert len(result.data.enrolled_students) == 1
        assert result.data.enrolled_students[0].id == student.id

    def test_delete_course(self, repository, course):
        result = repository.delete(ComplexDeleteRequest(id=course.id))

        assert isinstance(result, SuccessDTO)
        assert result.data.id == course.id

        # Verify course is deleted
        get_result = repository.get(ComplexGetRequest(id=course.id))
        assert not isinstance(get_result, SuccessDTO)

    def test_list_filter_by_department(self, repository, department):
        create_result = repository.create(ComplexCreateRequest(
            name="Department Test Course",
            department_id=department.id,
            syllabus=SyllabusCreateModel(
                name="Test Syllabus",
                content="Content"
            )
        ))
        assert isinstance(create_result, SuccessDTO)

        result = repository.list(ComplexListRequest(department_id=department.id))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) >= 1
        assert all(course.department.id == department.id for course in result.data)

    def test_update_assignments(self, repository, course, assignment):
        request = ComplexUpdateRequest(
            id=course.id,
            assignment_ids=[assignment.id]
        )
        result = repository.update(request)

        assert isinstance(result, SuccessDTO)
        assert len(result.data.assignments) == 1
        assert result.data.assignments[0].id == assignment.id

    def test_create_invalid_department(self, repository):
        request = ComplexCreateRequest(
            name="Invalid Course",
            department_id=99999,  # Non-existent department
            syllabus=SyllabusCreateModel(
                name="Test Syllabus",
                content="Content"
            )
        )
        result = repository.create(request)

        assert not isinstance(result, SuccessDTO)