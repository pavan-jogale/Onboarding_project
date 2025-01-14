"""Migration 5

Revision ID: 9580b14e1230
Revises: 723a1b97f4bd
Create Date: 2024-11-06 14:30:10.005808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9580b14e1230'
down_revision: Union[str, None] = '723a1b97f4bd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('pavan', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'pavan')
    # ### end Alembic commands ###
