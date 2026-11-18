"""Local email/password accounts in the shared PostgreSQL database."""

import sqlalchemy as sa

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "app_user",
        sa.Column("uid", sa.Uuid(), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "role IN ('USER', 'ADMIN', 'SUPERADMIN')", name=op.f("ck_app_user_role")
        ),
        sa.PrimaryKeyConstraint("uid", name="pk_app_user"),
        sa.UniqueConstraint("email", name="uq_app_user_email"),
    )


def downgrade():
    op.drop_table("app_user")
