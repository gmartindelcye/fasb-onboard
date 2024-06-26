"""Bank table

Revision ID: 93c85635fa5e
Revises: 03c9f373de3e
Create Date: 2024-04-04 13:10:53.700925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '93c85635fa5e'
down_revision: Union[str, None] = '03c9f373de3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bank',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_code'), 'bank', ['code'], unique=True)
    op.create_index(op.f('ix_bank_name'), 'bank', ['name'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_bank_name'), table_name='bank')
    op.drop_index(op.f('ix_bank_code'), table_name='bank')
    op.drop_table('bank')
    # ### end Alembic commands ###
