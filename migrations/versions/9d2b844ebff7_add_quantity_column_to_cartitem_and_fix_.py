"""Add quantity column to CartItem and fix id default

Revision ID: 9d2b844ebff7
Revises: a9368c2f65d6
Create Date: 2025-06-25 17:29:23.299872

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d2b844ebff7'
down_revision = 'a9368c2f65d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cart_item', schema=None) as batch_op:
        batch_op.drop_column('quantity')

    # ### end Alembic commands ###
