"""Create local accounts explicitly: python -m src.auth.manage --email you@example.com --role SUPERADMIN."""

import argparse
import asyncio
from getpass import getpass

from src.async_database import AsyncDatabase
from src.auth.config import AuthConfig
from src.auth.dal import UserDal
from src.auth.dto import RegisterRequest
from src.auth.local import LocalAuthService
from src.config import get_settings


async def create(email, role):
    config = AuthConfig()
    if config.AUTH_MODE != "local":
        raise SystemExit("Local accounts are disabled in OIDC mode")
    password = getpass("Password (12–128 characters): ")
    if password != getpass("Confirm password: "):
        raise SystemExit("Passwords do not match")
    body = RegisterRequest(email=email, password=password)
    db = AsyncDatabase(get_settings().database_url)
    try:
        principal = await LocalAuthService(config, UserDal(db)).create_user(body, role)
        print(f"Created {principal.subject} with role {role}")
    finally:
        await db.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a local user (requires database access)"
    )
    parser.add_argument("--email", required=True)
    parser.add_argument(
        "--role", choices=["USER", "ADMIN", "SUPERADMIN"], default="USER"
    )
    args = parser.parse_args()
    asyncio.run(create(args.email, args.role))
