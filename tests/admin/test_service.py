from unittest.mock import MagicMock

from src.admin.service import AdminService


class TestAdminService:
    def test_set_tournament_service_stores_reference(self):
        admin = AdminService()
        tournament_svc = MagicMock()
        admin.set_tournament_service(tournament_svc)
        assert admin._tournament_service is tournament_svc

    def test_tournament_service_initially_none(self):
        admin = AdminService()
        assert admin._tournament_service is None
