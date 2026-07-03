from dependency_injector import containers, providers

from src.admin.service import AdminService


class AdminContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["src.admin.routes"]
    )

    # TODO: inject domain-specific services from the root container, e.g.:
    # my_service = providers.Dependency()

    service = providers.Singleton(AdminService)
