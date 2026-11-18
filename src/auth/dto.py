from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, SecretStr, field_validator


class Principal(BaseModel):
    subject: str
    issuer: str
    roles: list[str]


class Credentials(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def bounded_password(cls, value):
        if not 1 <= len(value.get_secret_value()) <= 128:
            raise ValueError("Password must contain 1 to 128 characters")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return str(value).lower()


class RegisterRequest(Credentials):
    @field_validator("password")
    @classmethod
    def password_policy(cls, value):
        if not 12 <= len(value.get_secret_value()) <= 128:
            raise ValueError("Password must contain 12 to 128 characters")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
