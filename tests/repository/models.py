from datetime import datetime
from typing import List, Optional

from lib.core.models import BaseCoreModel


class PrimitiveCoreModel(BaseCoreModel):
    id: int | None = None
    name: str


class CategoryCoreModel(BaseCoreModel):
    id: int | None = None
    title: str
    description: str | None = None


class ComposedCoreModel(BaseCoreModel):
    id: int | None = None
    name: str
    description: str | None = None
    category: CategoryCoreModel
    created_at: datetime
    status: str = "active"


class SyllabusCoreModel(BaseCoreModel):
    id: int
    name: str
    content: str


class DepartmentCoreModel(BaseCoreModel):
    id: int
    name: str
    code: str


class AssignmentCoreModel(BaseCoreModel):
    id: int
    name: str
    description: str
    due_date: str


class StudentCoreModel(BaseCoreModel):
    id: int
    name: str
    email: str


class ComplexCoreModel(BaseCoreModel):
    id: int
    name: str
    description: Optional[str] = None

    # One-to-one relationship
    syllabus: SyllabusCoreModel

    # Many-to-one relationship
    department: DepartmentCoreModel

    # One-to-many relationship
    assignments: List[AssignmentCoreModel]

    # Many-to-many relationship
    enrolled_students: List[StudentCoreModel]
