from src.auth.config import AuthConfig


class AuthService:
    def __init__(self, config: AuthConfig) -> None:
        self._config = config

    def verify_client_secret(self, secret: str) -> bool:
        return secret == self._config.CLIENT_SHARED_SECRET

    def verify_admin_credentials(self, username: str, password: str) -> bool:
        return (
            username == self._config.ADMIN_USERNAME
            and password == self._config.ADMIN_PASSWORD
        )
