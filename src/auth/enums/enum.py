import enum


class AdminUserRole(str, enum.Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
