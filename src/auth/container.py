from dependency_injector import containers, providers

from src.async_database import AsyncDatabase
from src.auth.config import get_auth_config
from src.auth.dal import AuthDal
from src.auth.service import AuthService


class AuthContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.auth.dependencies", "src.auth.routes"]
    )

    config = providers.Singleton(get_auth_config)
    db_config = providers.Dependency()

    db = providers.Singleton(
        AsyncDatabase,
        url=db_config.provided.db_url.call("auth"),
        echo=db_config.provided.DB_ECHO,
        echo_pool=db_config.provided.DB_CONN_ECHO,
    )

    dal = providers.Factory(AuthDal, db=db)

    service = providers.Singleton(
        AuthService,
        config=config,
        dal=dal,
    )
