"""
HubGrep database models
"""

import json
import enum
import re
import logging

from typing import TYPE_CHECKING
from flask_security.models import fsqla_v2 as fsqla
from hubgrep import db
from hubgrep.lib.hosting_service_interfaces import hosting_service_interface_mapping
from hubgrep.lib.cached_session.cached_session import CachedSession

if TYPE_CHECKING:
    from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import HostingServiceInterface

logger = logging.getLogger(__name__)


# Define models
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    pass


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

    def set_service_label(self):
        self.label = re.split("//", self.api_url)[1].rstrip("/")

    def get_hosting_service_interface(self, cached_session: 'CachedSession', timeout: int) -> "HostingServiceInterface":
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
