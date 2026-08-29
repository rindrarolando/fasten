from src.log.context import (
    bind_log_context,
    get_log_context,
    get_request_id,
    reset_log_context,
    reset_request_id,
    set_request_id,
)


class TestRequestId:
    def test_defaults_to_none(self):
        assert get_request_id() is None

    def test_set_and_get(self):
        token = set_request_id("abc-123")
        try:
            assert get_request_id() == "abc-123"
        finally:
            reset_request_id(token)
        assert get_request_id() is None


class TestBindLogContext:
    def test_defaults_to_empty(self):
        assert get_log_context() == {}

    def test_bind_merges_kwargs(self):
        token = bind_log_context(user_id="u1")
        try:
            assert get_log_context() == {"user_id": "u1"}
        finally:
            reset_log_context(token)
        assert get_log_context() == {}

    def test_nested_bind_restores_previous_on_reset(self):
        outer_token = bind_log_context(job_name="sync")
        try:
            inner_token = bind_log_context(user_id="u1")
            try:
                assert get_log_context() == {"job_name": "sync", "user_id": "u1"}
            finally:
                reset_log_context(inner_token)
            assert get_log_context() == {"job_name": "sync"}
        finally:
            reset_log_context(outer_token)
        assert get_log_context() == {}
