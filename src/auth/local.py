import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from starlette.concurrency import run_in_threadpool

from src.auth.config import AuthConfig
from src.auth.dal import UserDal
from src.auth.dto import Credentials, Principal, RegisterRequest, TokenResponse
from src.auth.models import User

password_hash = PasswordHash.recommended()


class LocalAuthService:
    def __init__(self, config: AuthConfig, dal: UserDal):
        self.config = config
        self.dal = dal

    def unauthorized(self):
        return HTTPException(
            401,
            "Invalid credentials or access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def principal(self, user: User) -> Principal:
        return Principal(
            subject=str(user.uid), issuer=self.config.JWT_ISSUER, roles=[user.role]
        )

    async def create_user(self, body: RegisterRequest, role: str = "USER") -> Principal:
        hashed = await run_in_threadpool(
            password_hash.hash, body.password.get_secret_value()
        )
        try:
            user = await self.dal.create(
                User(
                    uid=uuid.uuid4(),
                    email=body.email,
                    password_hash=hashed,
                    role=role,
                    is_active=True,
                )
            )
        except IntegrityError:
            raise HTTPException(409, "Email already registered") from None
        return self.principal(user)

    async def login(self, body: Credentials) -> TokenResponse:
        user = await self.dal.get_by_email(body.email)
        # Perform a hash even for an unknown account to avoid a fast user-existence signal.
        if user is None:
            await run_in_threadpool(
                password_hash.hash, body.password.get_secret_value()
            )
            raise self.unauthorized()
        valid = await run_in_threadpool(
            password_hash.verify, body.password.get_secret_value(), user.password_hash
        )
        if not valid or not user.is_active:
            raise self.unauthorized()
        now = datetime.now(timezone.utc)
        token = jwt.encode(
            {
                "sub": str(user.uid),
                "iss": self.config.JWT_ISSUER,
                "aud": self.config.JWT_AUDIENCE,
                "iat": now,
                "exp": now + timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
            },
            self.config.JWT_SECRET_KEY.get_secret_value(),
            algorithm="HS256",
        )
        return TokenResponse(access_token=token)

    async def authenticate(self, token: str) -> Principal:
        try:
            claims = jwt.decode(
                token,
                self.config.JWT_SECRET_KEY.get_secret_value(),
                algorithms=["HS256"],
                issuer=self.config.JWT_ISSUER,
                audience=self.config.JWT_AUDIENCE,
                options={"require": ["sub", "iss", "aud", "exp", "iat"]},
            )
            uid = uuid.UUID(claims["sub"])
        except (jwt.PyJWTError, ValueError, TypeError, AttributeError):
            raise self.unauthorized() from None
        user = await self.dal.get_by_uid(uid)
        if user is None or not user.is_active:
            raise self.unauthorized()
        return self.principal(user)
