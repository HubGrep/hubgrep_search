import logging
import urllib.parse
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

    # id on the hosting_service
    foreign_id = db.Column(db.Integer)

    hosting_service_id = db.Column(
        db.Integer, db.ForeignKey("hosting_service.id"), nullable=False
    )
    hosting_service = db.relationship(
        "HostingService", backref=db.backref("repos", lazy=True)
    )

    namespace = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(500), nullable=False)

    description = db.Column(db.Text(), nullable=True)
    is_fork = db.Column(db.Boolean())
    homepage = db.Column(db.String(500), nullable=True)
    # url to the repo!
    html_url = db.Column(db.String(500), nullable=True)
    language = db.Column(db.String(500), nullable=True)
    forks_count = db.Column(db.Integer(), nullable=False)
    stars_count = db.Column(db.Integer(), nullable=False)
    size = db.Column(db.Integer(), nullable=False)
    open_issues_count = db.Column(db.Integer(), nullable=False)
    is_archived = db.Column(db.Boolean())
    is_disabled = db.Column(db.Boolean())
    pushed_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    subscribers_count = db.Column(db.Integer(), nullable=False)
    license_name = db.Column(db.String(500), nullable=True)

    @classmethod
    def from_dict(cls, d, hosting_service: 'HostingService'):
        if hosting_service.type == "gitea":
            return cls.from_gitea_dict(d, hosting_service)

    @classmethod
    def from_gitea_dict(cls, d, hosting_service):
        foreign_id = d["gitea_id"]
        r = cls.query.filter_by(
            hosting_service_id=hosting_service.id, foreign_id=foreign_id
        ).first()
        if not r:
            r = cls()
            r.hosting_service_id = hosting_service.id
            r.foreign_id = foreign_id
        r.name = d["name"]
        r.namespace = d["owner_username"]
        r.description = d["description"]
        r.subscribers_count = d['watchers_count']
        # r.is_empty = d["empty"]
        # d["private"] = self.private
        r.is_fork = d["fork"]
        # r.is_mirror = d["mirror"] = self.mirror
        r.size = d["size"]
        r.homepage = d["website"]
        path_to_user = urllib.parse.urljoin(hosting_service.landingpage_url, r.namespace + "/")
        r.html_url = urllib.parse.urljoin(path_to_user, r.name)
        r.stars_count = d["stars_count"]
        r.forks_count = d["forks_count"]
        r.watchers_count = d["watchers_count"]
        r.open_issues_count = d["open_issues_count"]
        r.default_branch = d["default_branch"]
        r.created_at = d["created_at"]
        r.updated_at = d["updated_at"]
        return r

    @classmethod
    def from_fake(cls, fake, hosting_service: "HostingService"):
        import faker
        from faker import Faker
        from faker.providers import lorem

        fake: Faker

        r = cls()
        r.hosting_service_id = hosting_service.id
        r.namespace = fake.name().replace(" ", "-")
        r.name = fake.sentence().replace(" ", "-")
        r.description = fake.sentence()
        r.is_fork = fake.random_element([True, False])
        r.homepage = ""
        r.html_url = ""
        r.language = fake.random_element(
            [
                "java",
                "pyhon",
                "c",
                "cpp",
                "javascript",
                "fortran",
                "html",
                "css",
                "scss",
                "bash",
            ]
        )
        r.forks_count = fake.random_int()
        r.stars_count = fake.random_int()
        r.watchers_count = fake.random_int()
        r.size = fake.random_int()
        r.open_issues_count = fake.random_int()
        r.is_archived = fake.random_element([True, False])
        r.is_disabled = fake.random_element([True, False])
        r.pushed_at = fake.date_time()
        r.created_at = fake.date_time()
        r.updated_at = fake.date_time()
        r.subscribers_count = fake.random_int()
        r.license_name = fake.random_element(["mit", "agpl", "gpl", "apache"])
        return r
