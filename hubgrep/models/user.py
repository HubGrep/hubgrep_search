import logging

from flask_security.models import fsqla_v2 as fsqla
from hubgrep import db


logger = logging.getLogger(__name__)


# Define models
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    pass
