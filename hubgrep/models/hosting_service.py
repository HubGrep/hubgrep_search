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
   
    export_timestamp = db.Column(db.DateTime)
    repo_count = db.Column(db.Integer)

    @property
    def domain(self):
        return re.split("//", self.landingpage_url)[1].rstrip("/")

    def to_dict(self):
        return dict(
                    type=self.type,
                    landingpage_url=self.landingpage_url,
                    api_url=self.api_url,
                )
    
