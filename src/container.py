from dependency_injector import containers, providers

from src.admin.container import AdminContainer
from src.async_database import AsyncDatabase
from src.auth.container import AuthContainer
from src.config import get_settings


class RootContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["src.auth.dependencies"])
    settings = providers.Singleton(get_settings)
    db = providers.Singleton(
        AsyncDatabase,
        url=settings.provided.database_url,
        echo=settings.provided.DB_ECHO,
    )
    auth = providers.Container(AuthContainer)
    admin = providers.Container(AdminContainer)
    # New domains receive this same database:
    # product = providers.Container(ProductContainer, db=db)
