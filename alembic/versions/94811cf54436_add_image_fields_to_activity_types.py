"""add image fields to activity types

Revision ID: 94811cf54436
Revises: 5b3fa8755fe8
Create Date: 2026-10-16 11:49:27.629483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94811cf54436'
down_revision: Union[str, Sequence[str], None] = '5b3fa8755fe8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('activity_types', sa.Column('image_url', sa.String(), nullable=True))
    op.add_column('activity_types', sa.Column('image_public_id', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('activity_types', 'image_public_id')
    op.drop_column('activity_types', 'image_url')
