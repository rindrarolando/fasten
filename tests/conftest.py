import os

# Configuration only; tests never contact the example provider or production DB.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://fasten:test@localhost:5432/fasten_test")
os.environ.setdefault("OIDC_ISSUER", "https://issuer.test")
os.environ.setdefault("OIDC_AUDIENCE", "fasten-api")
