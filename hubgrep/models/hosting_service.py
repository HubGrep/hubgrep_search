"""
HostingService model and related
"""
import json
import enum
import re
import logging

from typing import TYPE_CHECKING
from hubgrep import db

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

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("hosting_services", lazy=True))

    type = db.Column(db.String(80), nullable=False)

    # main instance website
    landingpage_url = db.Column(db.String(500))

    # should this be unique, or can we use it to store multiple
    # api keys for a backend?
    api_url = db.Column(db.String(500), unique=True, nullable=False)

    # individual config for a specific service (eg. api-key)
    # could be json, but thats only supported for postgres
    config = db.Column(db.Text)

    # frontend label
    label = db.Column(db.String(80))
    
    has_local_index = db.Column(db.Boolean, default=False)

    def set_service_label(self):
        self.label = re.split("//", self.landingpage_url)[1].rstrip("/")

    def get_hosting_service_interface(
        self, cached_session: "CachedSession", timeout: int
    ) -> "HostingServiceInterface":
        from hubgrep.lib.hosting_service_interfaces import (
            hosting_service_interface_mapping,
        )

        config_str = self.config
        config = json.loads(config_str)

        HostingInterfaceClass = hosting_service_interface_mapping[self.type]
        hosting_service_interface = HostingInterfaceClass(
            self.id,
            self.api_url,
            self.label,
            config,
            cached_session,
            timeout,
        )
        return hosting_service_interface
