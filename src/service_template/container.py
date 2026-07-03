from dependency_injector import containers, providers

from src.async_database import AsyncDatabase
from src.service_template.dal import ServiceDal
from src.service_template.service import ServiceLayer
from src.service_template.services.example_worker import ExampleWorker


# TODO: rename this class to match your service, e.g. ProductContainer.
class ServiceContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        # TODO: update the module path once you rename the package.
        modules=["src.service_template.routes"]
    )

    db_config = providers.Dependency()

    db = providers.Singleton(
        AsyncDatabase,
        # TODO: replace "service_template" with your service name so the URL
        #       resolves to <service_name>_db / <service_name>_user.
        url=db_config.provided.db_url.call("service_template"),
        echo=db_config.provided.DB_ECHO,
        echo_pool=db_config.provided.DB_CONN_ECHO,
    )

    dal = providers.Factory(ServiceDal, db=db)

    example_worker = providers.Factory(ExampleWorker, dal=dal)

    service = providers.Factory(
        ServiceLayer,
        dal=dal,
        example_worker=example_worker,
    )
