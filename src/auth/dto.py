from pydantic import BaseModel


class Principal(BaseModel):
    subject: str
    issuer: str
    roles: list[str]
