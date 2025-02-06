from typing import List

from lib.sdk.core.dto import SuccessDTO, SuccessListDTO
from lib.sdk.core.error import BaseError, ErrorType
from tests.repository.composed.composed_secondary_entities import (
    ComposedCreateRequest,
    ComposedListRequest,
    ComposedTestSetup,
    ComposedRepository,
    ComposedListDTO,
    ComposedCreateDTO,
)
from tests.repository.models import CategoryCoreModel, ComposedCoreModel


class TestComposedListFilters(ComposedTestSetup):
    def test_list_filter_by_name(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        create_result_1: ComposedCreateDTO = repository.create(
            ComposedCreateRequest(name="Target Item", category_id=category.id)
        )

        if isinstance(create_result_1, BaseError):
            raise ValueError(f"Failed to create test item: {create_result_1.message}")

        create_result_2: ComposedCreateDTO = repository.create(
            ComposedCreateRequest(name="Other Item", category_id=category.id)
        )

        if isinstance(create_result_2, BaseError):
            raise ValueError(f"Failed to create test item: {create_result_2.message}")

        result: ComposedListDTO = repository.list(ComposedListRequest(name="Target Item"))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Target Item"

    def test_list_filter_by_status(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        create_result_1: ComposedCreateDTO = repository.create(
            ComposedCreateRequest(name="Active Item", category_id=category.id, status="active")
        )
        if isinstance(create_result_1, BaseError):
            raise ValueError(f"Failed to create active item: {create_result_1.message}")

        create_result_2: ComposedCreateDTO = repository.create(
            ComposedCreateRequest(name="Inactive Item", category_id=category.id, status="inactive")
        )
        if isinstance(create_result_2, BaseError):
            raise ValueError(f"Failed to create inactive item: {create_result_2.message}")

        result: ComposedListDTO = repository.list(ComposedListRequest(status="inactive"))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].status == "inactive"


class TestComposedListPagination(ComposedTestSetup):
    def test_pagination_limit(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        for i in range(5):
            result: ComposedCreateDTO = repository.create(
                ComposedCreateRequest(name=f"Item {i}", category_id=category.id)
            )
            if isinstance(result, BaseError):
                raise ValueError(f"Failed to create test item {i}: {result.message}")

        list_result: ComposedListDTO = repository.list(ComposedListRequest(page=1, page_size=2))

        assert isinstance(list_result, SuccessDTO)
        assert len(list_result.data) == 2

    def test_pagination_offset(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        items: List[ComposedCoreModel] = []
        for i in range(3):
            created: ComposedCreateDTO = repository.create(
                ComposedCreateRequest(name=f"Item {i}", category_id=category.id)
            )
            if isinstance(created, BaseError):
                raise ValueError(f"Failed to create test item {i}: {created.message}")
            items.append(created.data)

        result: ComposedListDTO = repository.list(ComposedListRequest(page=2, page_size=1))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Item 1"

    def test_filters(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        for i in range(4):
            result: ComposedCreateDTO = repository.create(
                ComposedCreateRequest(name=f"Test {i}", category_id=category.id, status="active")
            )
            if isinstance(result, BaseError):
                raise ValueError(f"Failed to create test item {i}: {result.message}")

        list_result: ComposedListDTO = repository.list(
            ComposedListRequest(
                status="active",
                name="Test 1",
            )
        )

        assert isinstance(list_result, SuccessDTO)
        assert len(list_result.data) == 1
        assert list_result.data[0].name == "Test 1"


class TestComposedListPaginationValidation(ComposedTestSetup):
    def test_has_next_page_single_page(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        result: ComposedListDTO = repository.list(ComposedListRequest(page=1, page_size=10))

        assert isinstance(result, SuccessListDTO)
        assert result.has_next_page is False
        assert len(result.data) < 10

    def test_has_next_page_multiple_pages(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        for i in range(11):
            result: ComposedCreateDTO = repository.create(
                ComposedCreateRequest(name=f"Item {i}", category_id=category.id)
            )
            if isinstance(result, BaseError):
                raise ValueError(f"Failed to create test item {i}: {result.message}")

        list_result: ComposedListDTO = repository.list(ComposedListRequest(page=1, page_size=10))

        assert isinstance(list_result, SuccessListDTO)
        assert list_result.has_next_page is True
        assert len(list_result.data) == 10

    def test_has_next_page_last_page(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        for i in range(15):
            result: ComposedCreateDTO = repository.create(
                ComposedCreateRequest(name=f"Item {i}", category_id=category.id)
            )
            if isinstance(result, BaseError):
                raise ValueError(f"Failed to create test item {i}: {result.message}")

        list_result: ComposedListDTO = repository.list(ComposedListRequest(page=2, page_size=10))

        assert isinstance(list_result, SuccessListDTO)
        assert list_result.has_next_page is False
        assert len(list_result.data) == 5

    def test_has_next_page_empty_result(self, repository: ComposedRepository) -> None:
        result: ComposedListDTO = repository.list(ComposedListRequest(page=1, page_size=10))

        assert isinstance(result, SuccessListDTO)
        assert result.has_next_page is False
        assert len(result.data) == 0

    def test_has_next_page_no_pagination(self, repository: ComposedRepository, category: CategoryCoreModel) -> None:
        result: ComposedCreateDTO = repository.create(ComposedCreateRequest(name="Test Item", category_id=category.id))
        if isinstance(result, BaseError):
            raise ValueError(f"Failed to create test item: {result.message}")

        list_result: ComposedListDTO = repository.list(ComposedListRequest())

        assert isinstance(list_result, SuccessListDTO)
        assert list_result.has_next_page is None
        assert len(list_result.data) > 0
