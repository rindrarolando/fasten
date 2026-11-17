from dependency_injector import containers, providers

from src.auth.config import AuthConfig
from src.auth.service import AuthService


class AuthContainer(containers.DeclarativeContainer):
    config = providers.Singleton(AuthConfig)
    service = providers.Singleton(AuthService, config=config)
