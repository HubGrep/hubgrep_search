import datetime
import logging
import os
import click
import json
from hubgrep.cli_blueprint import cli_bp

from hubgrep import redis_client
from hubgrep import db, security
from flask_security import hash_password

from hubgrep.models import User, HostingService


logger = logging.getLogger(__name__)


def create_admin(admin_email, admin_password):
    admin = security.datastore.find_user(email=admin_email)
    if not admin:
        admin = security.datastore.create_user(
            email=admin_email, password=hash_password(admin_password)
        )
    admin.confirmed_at = datetime.datetime.now()
    return admin


@cli_bp.cli.command()
def init():
    admin_email = os.environ["HUBGREP_ADMIN_EMAIL"]
    admin_password = os.environ["HUBGREP_ADMIN_PASSWORD"]

    admin = create_admin(admin_email, admin_password)

    admin_role = security.datastore.find_or_create_role("admin", permissions=["admin"])

    security.datastore.add_role_to_user(admin, admin_role)

    db.session.commit()

