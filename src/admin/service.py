class AdminService:
    """
    Orchestrates admin-level operations across other services.
    No direct DB access — delegates to injected service instances.

    TODO: inject domain-specific services via __init__ and wire them
    from AdminContainer once your services are registered.
    """

    def __init__(self) -> None:
        pass
