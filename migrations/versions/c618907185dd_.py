"""empty message

Revision ID: c618907185dd
Revises: f86929547152
Create Date: 2021-03-28 11:04:40.789755

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm.session import Session

# revision identifiers, used by Alembic.
revision = 'c618907185dd'
down_revision = 'f86929547152'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hosting_service', sa.Column('label', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###
    session = Session(bind=op.get_bind())
    for service in session.query(HostingService).all():
        service.set_service_label()
    session.commit()


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hosting_service', 'label')
    # ### end Alembic commands ###
