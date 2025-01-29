from lib.core.dto import SuccessDTO
from lib.core.error import BaseError, ErrorType
from tests.repository.composed.composed_secondary_entities import ComposedCreateRequest, ComposedListRequest, \
    ComposedTestSetup


class TestComposedListFilters(ComposedTestSetup):
    def test_list_filter_by_name(self, repository, category):
        create_result_1 = repository.create(ComposedCreateRequest(
            name="Target Item",
            category_id=category.id
        ))

        assert isinstance(create_result_1, SuccessDTO)

        create_result_2 = repository.create(ComposedCreateRequest(
            name="Other Item",
            category_id=category.id
        ))

        assert isinstance(create_result_2, SuccessDTO)

        result = repository.list(ComposedListRequest(name="Target Item"))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Target Item"

    def test_list_filter_by_status(self, repository, category):
        repository.create(ComposedCreateRequest(
            name="Active Item",
            category_id=category.id,
            status="active"
        ))
        repository.create(ComposedCreateRequest(
            name="Inactive Item",
            category_id=category.id,
            status="inactive"
        ))

        result = repository.list(ComposedListRequest(status="inactive"))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].status == "inactive"


class TestComposedListPagination(ComposedTestSetup):
    def test_pagination_limit(self, repository, category):
        for i in range(5):
            repository.create(ComposedCreateRequest(
                name=f"Item {i}",
                category_id=category.id
            ))

        result = repository.list(ComposedListRequest(page=1, page_size=2))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 2

    def test_pagination_offset(self, repository, category):
        items = []
        for i in range(3):
            created = repository.create(ComposedCreateRequest(
                name=f"Item {i}",
                category_id=category.id
            ))
            items.append(created.data)

        result = repository.list(ComposedListRequest(page=2, page_size=1))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Item 1"

    def test_filters(self, repository, category):
        for i in range(4):
            repository.create(ComposedCreateRequest(
                name=f"Test {i}",
                category_id=category.id,
                status="active"
            ))

        result = repository.list(ComposedListRequest(
            status="active",
            name="Test 1",
        ))

        assert isinstance(result, SuccessDTO)
        assert len(result.data) == 1
        assert result.data[0].name == "Test 1"


class TestComposedListPaginationValidation(ComposedTestSetup):
    def test_negative_page(self, repository, category):
        result = repository.list(ComposedListRequest(page=-1))

        assert isinstance(result, BaseError)
        assert result.error_type == ErrorType.VALIDATION
        assert "page" in result.context
        assert result.context["page"] == -1

    def test_zero_page(self, repository, category):
        result = repository.list(ComposedListRequest(page=0))

        assert isinstance(result, BaseError)
        assert result.error_type == ErrorType.VALIDATION
        assert "page" in result.context
        assert result.context["page"] == 0

    def test_zero_page_size(self, repository, category):
        result = repository.list(ComposedListRequest(page=1, page_size=0))

        assert isinstance(result, BaseError)
        assert result.error_type == ErrorType.VALIDATION
        assert "page_size" in result.context
        assert result.context["page_size"] == 0

    def test_negative_page_size(self, repository, category):
        result = repository.list(ComposedListRequest(page=1, page_size=-10))

        assert isinstance(result, BaseError)
        assert result.error_type == ErrorType.VALIDATION
        assert "page_size" in result.context
        assert result.context["page_size"] == -10

