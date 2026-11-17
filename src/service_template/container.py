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

    # Inject RootContainer.db; domains never own engines or database credentials.
    db = providers.Dependency(instance_of=AsyncDatabase)

    dal = providers.Factory(ServiceDal, db=db)

    example_worker = providers.Factory(ExampleWorker, dal=dal)

    service = providers.Factory(
        ServiceLayer,
        dal=dal,
        example_worker=example_worker,
    )
