"""empty message

Revision ID: 691fa93dfbcc
Revises: d9b3964977e4
Create Date: 2021-07-05 23:38:52.702398

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '691fa93dfbcc'
down_revision = 'd9b3964977e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('repositories', 'open_issues_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('repositories', 'open_issues_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
