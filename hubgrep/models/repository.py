import logging
from hubgrep import db
from sqlalchemy import Index, Identity

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hubgrep.models.hosting_service import HostingService

logger = logging.getLogger(__name__)


class Repository(db.Model):
    __tablename__ = "repositories"

    __table_args__ = (
        #Index("hosting_service_id_index", "hosting_service_id"),
        # UNLOGGED prevents wal write (as we will never edit the table, it should be fine?)
        {"prefixes": ["UNLOGGED"]},
    )

    # use identity to avoid reusing same sequence when we copy this table:
    # https://stackoverflow.com/a/12265248
    id = db.Column(db.Integer, Identity(), primary_key=True)

    # id on the hosting_service
    foreign_id = db.Column(db.Integer)

    hosting_service_id = db.Column(
        db.Integer,
        db.ForeignKey("hosting_service.id"),
        nullable=True,
    )
    hosting_service = db.relationship(
        "HostingService", backref=db.backref("repos", lazy=True)
    )

    name = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text(), nullable=True)

    created_at = db.Column(db.DateTime(), nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True)
    pushed_at = db.Column(db.DateTime(), nullable=True)

    stars_count = db.Column(db.Integer(), nullable=True)
    forks_count = db.Column(db.Integer(), nullable=True)

    is_private = db.Column(db.Boolean())
    is_fork = db.Column(db.Boolean())
    is_archived = db.Column(db.Boolean())
    is_disabled = db.Column(db.Boolean())
    is_mirror = db.Column(db.Boolean())
    homepage_url = db.Column(db.String(500), nullable=True)
    repo_url = db.Column(db.String(500), nullable=True)

    # language = db.Column(db.String(500), nullable=True)
    # size = db.Column(db.Integer(), nullable=True)
    # open_issues_count = db.Column(db.Integer(), nullable=True)
    # subscribers_count = db.Column(db.Integer(), nullable=True)
    # license_name = db.Column(db.String(500), nullable=True)
