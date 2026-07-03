from src.utils import PaginatedResponse, paginate, utcnow


class TestUtcnow:
    def test_returns_timezone_aware_datetime(self):
        dt = utcnow()
        assert dt.tzinfo is not None


class TestPaginate:
    async def test_wraps_items_and_total(self):
        @paginate(default_limit=50)
        async def fetch(page: int, size: int) -> tuple[list[str], int]:
            return ["a", "b"], 10

        result = await fetch(page=2, size=5)
        assert isinstance(result, PaginatedResponse)
        assert result.items == ["a", "b"]
        assert result.total == 10
        assert result.page == 2
        assert result.size == 5

    async def test_uses_default_limit_when_size_is_none(self):
        @paginate(default_limit=25)
        async def fetch(page: int, size: int) -> tuple[list[int], int]:
            assert size == 25
            return [1], 1

        result = await fetch(page=1, size=None)
        assert result.size == 25
