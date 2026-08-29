from src.log import get_feature_logger

logger = get_feature_logger(__name__, feature="admin")


class AdminService:
    """
    Orchestrates admin-level operations across other services.
    No direct DB access — delegates to injected service instances.

    TODO: inject domain-specific services via __init__ and wire them
    from AdminContainer once your services are registered. Decorate public
    methods with @operation_log("...", feature="admin") as they're added.
    """

    def __init__(self) -> None:
        pass
