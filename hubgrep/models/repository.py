import logging

from hubgrep import db

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hubgrep.models.hosting_service import HostingService

logger = logging.getLogger(__name__)


class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    hosting_service_id = db.Column(db.Integer, db.ForeignKey("hosting_service.id"), nullable=False)
    hosting_service = db.relationship("HostingService", backref=db.backref("repos", lazy=True))

    namespace = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(500), nullable=False)

    description = db.Column(db.Text(), nullable=True)
    is_fork = db.Column(db.Boolean())
    homepage = db.Column(db.String(500), nullable=True)
    html_url = db.Column(db.String(500), nullable=True)
    language = db.Column(db.String(500), nullable=True)
    forks_count = db.Column(db.Integer(), nullable=False)
    stars_count = db.Column(db.Integer(), nullable=False)
    watchers_count = db.Column(db.Integer(), nullable=False)
    size = db.Column(db.Integer(), nullable=False)
    open_issues_count = db.Column(db.Integer(), nullable=False)
    is_archived = db.Column(db.Boolean())
    is_disabled = db.Column(db.Boolean())
    pushed_at = db.Column(db.DateTime())
    created_at = db.Column(db.DateTime())
    updated_at = db.Column(db.DateTime())
    subscribers_count = db.Column(db.Integer(), nullable=False)
    license_name = db.Column(db.String(500), nullable=True)

    @staticmethod
    def from_fake(fake, hosting_service: "HostingService"):
        import faker
        from faker import Faker
        from faker.providers import lorem
        fake: Faker
        
        r = Repository()
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
