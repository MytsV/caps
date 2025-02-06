from lib.sdk.infrastructure.repository.sqla.database import Base
from lib.sdk.infrastructure.repository.sqla.models import SoftSqlaModelBase
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from tests.repository.models import (
    PrimitiveCoreModel,
    CategoryCoreModel,
    ComposedCoreModel,
    SyllabusCoreModel,
    DepartmentCoreModel,
    AssignmentCoreModel,
    StudentCoreModel,
    ComplexCoreModel,
)


class PrimitiveSqlaModel(SoftSqlaModelBase):
    __tablename__ = "primitive_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def to_core_model(self) -> PrimitiveCoreModel:
        return PrimitiveCoreModel(id=self.id, name=self.name)


class CategorySqlaModel(SoftSqlaModelBase):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String, nullable=True)

    def to_core_model(self) -> CategoryCoreModel:
        return CategoryCoreModel(id=self.id, title=self.title, description=self.description)


class ComposedSqlaModel(SoftSqlaModelBase):
    __tablename__ = "complex_items"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    status = Column(String, default="active")

    category = relationship("CategorySqlaModel")

    def to_core_model(self) -> ComposedCoreModel:
        return ComposedCoreModel(
            id=self.id,
            name=self.name,
            description=self.description,
            category=self.category.to_core_model() if self.category else None,
            created_at=self.created_at,
            status=self.status,
        )


course_student_association = Table(
    "course_student",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("student_id", Integer, ForeignKey("students.id")),
)


class SyllabusSqlaModel(SoftSqlaModelBase):
    __tablename__ = "syllabuses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"), unique=True)
    course = relationship("ComplexSqlaModel", back_populates="syllabus")

    def to_core_model(self) -> SyllabusCoreModel:
        return SyllabusCoreModel(id=self.id, name=self.name, content=self.content)


class DepartmentSqlaModel(SoftSqlaModelBase):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    courses = relationship("ComplexSqlaModel", back_populates="department")

    def to_core_model(self) -> DepartmentCoreModel:
        return DepartmentCoreModel(id=self.id, name=self.name, code=self.code)


class AssignmentSqlaModel(SoftSqlaModelBase):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    due_date = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))
    course = relationship("ComplexSqlaModel", back_populates="assignments")

    def to_core_model(self) -> AssignmentCoreModel:
        return AssignmentCoreModel(id=self.id, name=self.name, description=self.description, due_date=self.due_date)


class StudentSqlaModel(SoftSqlaModelBase):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    courses = relationship("ComplexSqlaModel", secondary=course_student_association, back_populates="enrolled_students")

    def to_core_model(self) -> StudentCoreModel:
        return StudentCoreModel(id=self.id, name=self.name, email=self.email)


class ComplexSqlaModel(SoftSqlaModelBase):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)

    # One-to-one relationship
    syllabus = relationship("SyllabusSqlaModel", uselist=False, back_populates="course")

    # Many-to-one relationship
    department_id = Column(Integer, ForeignKey("departments.id"))
    department = relationship("DepartmentSqlaModel", back_populates="courses")

    # One-to-many relationship
    assignments = relationship("AssignmentSqlaModel", back_populates="course")

    # Many-to-many relationship
    enrolled_students = relationship("StudentSqlaModel", secondary=course_student_association, back_populates="courses")

    def to_core_model(self) -> ComplexCoreModel:
        return ComplexCoreModel(
            id=self.id,
            name=self.name,
            description=self.description,
            syllabus=self.syllabus.to_core_model() if self.syllabus else None,
            department=self.department.to_core_model() if self.department else None,
            assignments=[assignment.to_core_model() for assignment in self.assignments],
            enrolled_students=[student.to_core_model() for student in self.enrolled_students],
        )
