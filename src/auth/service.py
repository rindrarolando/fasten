from src.auth.config import AuthConfig
from src.log import get_feature_logger, operation_log

logger = get_feature_logger(__name__, feature="auth")


class AuthService:
    def __init__(self, config: AuthConfig) -> None:
        self._config = config

    @operation_log("verify_client_secret", feature="auth")
    def verify_client_secret(self, secret: str) -> bool:
        return secret == self._config.CLIENT_SHARED_SECRET

    @operation_log("verify_admin_credentials", feature="auth")
    def verify_admin_credentials(self, username: str, password: str) -> bool:
        return (
            username == self._config.ADMIN_USERNAME
            and password == self._config.ADMIN_PASSWORD
        )
