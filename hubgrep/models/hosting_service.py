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
   
    # frontend label
    label = db.Column(db.String(80))

    def set_service_label(self):
        self.label = re.split("//", self.landingpage_url)[1].rstrip("/")

    def to_dict(self):
        return dict(
                    type=self.type,
                    landingpage_url=self.landingpage_url,
                    api_url=self.api_url,
                )
    
