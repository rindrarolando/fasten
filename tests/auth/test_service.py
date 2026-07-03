from src.auth.service import AuthService


class TestVerifyClientSecret:
    def test_returns_true_for_matching_secret(self, auth_service: AuthService):
        assert auth_service.verify_client_secret("test-secret") is True

    def test_returns_false_for_wrong_secret(self, auth_service: AuthService):
        assert auth_service.verify_client_secret("wrong") is False

    def test_returns_false_for_empty_secret(self, auth_service: AuthService):
        assert auth_service.verify_client_secret("") is False


class TestVerifyAdminCredentials:
    def test_returns_true_for_valid_credentials(self, auth_service: AuthService):
        assert auth_service.verify_admin_credentials("admin", "admin-pass") is True

    def test_returns_false_for_wrong_username(self, auth_service: AuthService):
        assert auth_service.verify_admin_credentials("other", "admin-pass") is False

    def test_returns_false_for_wrong_password(self, auth_service: AuthService):
        assert auth_service.verify_admin_credentials("admin", "wrong") is False
