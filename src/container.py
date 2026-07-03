from dependency_injector import containers, providers

from src.config import get_db_config
from src.auth.container import AuthContainer
from src.admin.container import AdminContainer
# TODO: import your service containers here, e.g.:
# from src.my_service.container import MyServiceContainer


class RootContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.auth.dependencies",
            "src.admin.routes",
            # TODO: add your service routes module here, e.g.:
            # "src.my_service.routes",
        ]
    )

    db_config = providers.Singleton(get_db_config)

    auth = providers.Container(AuthContainer)

    admin = providers.Container(AdminContainer)
    # TODO: register your service container here, e.g.:
    # my_service = providers.Container(
    #     MyServiceContainer,
    #     db_config=db_config,
    # )
    # Then inject it into admin if needed:
    # admin = providers.Container(
    #     AdminContainer,
    #     my_service=my_service.service,
    # )
