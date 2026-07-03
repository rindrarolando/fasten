from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service_template.dal import ServiceDal


# TODO: rename to reflect its purpose (e.g. NotificationSender, ReportBuilder).
#       Inject it into ServiceLayer via ServiceContainer.
class ExampleWorker:
    """Example sub-service — handles a specific slice of domain logic."""

    def __init__(self, dal: "ServiceDal") -> None:
        self._dal = dal

    async def do_work(self) -> None:
        # TODO: implement domain logic here.
        pass
