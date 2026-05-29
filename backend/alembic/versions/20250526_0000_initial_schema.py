"""Initial schema migration (placeholder).

This is a starting point. After the DB agent seeds the SQLite file,
run the following to generate a proper migration:

    cd backend
    alembic revision --autogenerate -m "initial schema from models"

Then review and apply:
    alembic upgrade head

Revision ID: 20250526_0000
Revises: 
Create Date: 2026-05-26
"""



# revision identifiers, used by Alembic.
revision = '20250526_0000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The real schema is managed via the consolidated data/futon_manufacturing_sqlite.sql
    # This migration is intentionally minimal. Use autogenerate after first DB creation.
    pass


def downgrade() -> None:
    pass
