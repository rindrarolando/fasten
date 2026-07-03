from dependency_injector import containers, providers

from src.auth.config import get_auth_config
from src.auth.service import AuthService


class AuthContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.auth.dependencies"]
    )

    config = providers.Singleton(get_auth_config)

    service = providers.Singleton(
        AuthService,
        config=config,
    )
