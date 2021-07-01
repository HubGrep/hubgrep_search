"""
HostingService model and related
"""
import json
import enum
import re
import logging

from typing import TYPE_CHECKING
from hubgrep import db
from hubgrep.lib.hosting_service_interfaces import hosting_service_interface_mapping

if TYPE_CHECKING:
    from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
        HostingServiceInterface,
        CachedSession
    )


logger = logging.getLogger(__name__)


# todo
class HosterType(enum.Enum):
    github = 0
    gitlab = 1
    gitea = 2


class HostingService(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    user = db.relationship("User", backref=db.backref("hosting_services", lazy=True))

    type = db.Column(db.String(80), nullable=False)

    # main instance website
    landingpage_url = db.Column(db.String(500))

    api_url = db.Column(db.String(500), unique=True, nullable=False)

    # custom config for a service.
    # not used, so far (but it used to hold the api_key, which is a separate field now)
    custom_config = db.Column(db.Text)
   
    # we need an api key for github and gitlab
    api_key = db.Column(db.String(500), nullable=True)

    # frontend label
    label = db.Column(db.String(80))

    has_local_index = db.Column(db.Boolean, default=False)

    def set_service_label(self):
        self.label = re.split("//", self.landingpage_url)[1].rstrip("/")

    def to_dict(self):
        return dict(
                    type=self.type,
                    landingpage_url=self.landingpage_url,
                    api_url=self.api_url,
                )
    
    def get_hosting_service_interface(self, cached_session: 'CachedSession', timeout: int) -> "HostingServiceInterface":
        # todo: add this, when we know what to do with it :P
        #custom_config_str = self.custom_config
        #custom_config = json.loads(custom_config_str)

        HostingInterfaceClass = hosting_service_interface_mapping[self.type]
        hosting_service_interface = HostingInterfaceClass(
            self.id,
            self.api_url,
            self.label,
            self.api_key,
            cached_session,
            timeout,
        )
        return hosting_service_interface

    def to_dict(self):
        return dict(
                    type=self.type,
                    landingpage_url=self.landingpage_url,
                    api_url=self.api_url,
                )
