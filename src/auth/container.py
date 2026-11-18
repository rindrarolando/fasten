from dependency_injector import containers, providers

from src.auth.config import AuthConfig
from src.auth.dal import UserDal
from src.auth.local import LocalAuthService
from src.auth.service import AuthService


def build_service(config, db):
    if config.AUTH_MODE == "oidc":
        return AuthService(config)
    return LocalAuthService(config, UserDal(db))


class AuthContainer(containers.DeclarativeContainer):
    db = providers.Dependency()
    config = providers.Singleton(AuthConfig)
    service = providers.Singleton(build_service, config=config, db=db)
