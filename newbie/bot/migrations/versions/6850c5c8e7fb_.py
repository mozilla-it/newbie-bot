"""empty message

Revision ID: 6850c5c8e7fb
Revises: 1d5351822d50
Create Date: 2019-01-08 14:37:31.247705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6850c5c8e7fb'
down_revision = '1d5351822d50'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # op.add_column('admin', sa.Column('team', sa.String(length=100), nullable=True))
    op.add_column('messages', sa.Column('emp_type', sa.String(length=10), nullable=True))
    op.add_column('messages', sa.Column('location', sa.String(length=50), nullable=True))
    op.drop_column('messages', 'frequency')
    op.drop_column('messages', 'number_of_sends')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('number_of_sends', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('messages', sa.Column('frequency', sa.VARCHAR(length=5), autoincrement=False, nullable=True))
    op.drop_column('messages', 'location')
    op.drop_column('messages', 'emp_type')
    op.drop_column('admin', 'team')
    # ### end Alembic commands ###
