"""empty message

Revision ID: f86929547152
Revises: 167e105549bf
Create Date: 2021-03-26 11:52:11.009307

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f86929547152'
down_revision = '167e105549bf'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('hosting_service_base_url_key', 'hosting_service', type_='unique')
    op.alter_column('hosting_service', 'frontpage_url', new_column_name='landingpage_url')
    op.alter_column('hosting_service', 'base_url', new_column_name='api_url')
    op.create_unique_constraint(None, 'hosting_service', ['api_url'])


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hosting_service', sa.Column('base_url', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    op.add_column('hosting_service', sa.Column('frontpage_url', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'hosting_service', type_='unique')
    op.create_unique_constraint('hosting_service_base_url_key', 'hosting_service', ['base_url'])
    op.alter_column('hosting_service', 'landingpage_url', new_column_name='frontpage_url')
    op.alter_column('hosting_service', 'api_url', new_column_name='base_url')