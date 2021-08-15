"""
HostingService model and related
"""
import re
import logging

from hubgrep import db

logger = logging.getLogger(__name__)


class HostingService(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    type = db.Column(db.String(80), nullable=False)

    # main instance website
    landingpage_url = db.Column(db.String(500))

    api_url = db.Column(db.String(500), unique=True, nullable=False)
    domain = db.Column(db.String(500))

    export_timestamp = db.Column(db.DateTime)
    repo_count = db.Column(db.Integer)

    def set_domain(self):
        self.domain = re.split("//", self.landingpage_url)[1].rstrip("/")

    def to_dict(self):
        return dict(
            type=self.type,
            landingpage_url=self.landingpage_url,
            api_url=self.api_url,
        )

    @classmethod
    def from_dict(cls, d: dict):
        api_url = d["api_url"]
        hosting_service = HostingService.query.filter_by(api_url=api_url).first()
        if not hosting_service:
            hosting_service = cls()

        hosting_service.api_url = d["api_url"]
        hosting_service.landingpage_url = d["landingpage_url"]
        hosting_service.type = d["type"]
        hosting_service.set_domain()
        return hosting_service

