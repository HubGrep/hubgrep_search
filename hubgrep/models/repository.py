import logging
from hubgrep import db
from sqlalchemy import Index

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from hubgrep.models.hosting_service import HostingService

logger = logging.getLogger(__name__)


class Repository(db.Model):
    __tablename__ = "repositories"
    __table_args__ = (Index("repo_index", "foreign_id", "hosting_service_id"),)

    id = db.Column(db.Integer, primary_key=True)
    # set to true when import is finished
    imported = db.Column(db.Boolean, nullable=True, default=False)

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

    #language = db.Column(db.String(500), nullable=True)
    #size = db.Column(db.Integer(), nullable=True)
    #open_issues_count = db.Column(db.Integer(), nullable=True)
    #subscribers_count = db.Column(db.Integer(), nullable=True)
    #license_name = db.Column(db.String(500), nullable=True)
