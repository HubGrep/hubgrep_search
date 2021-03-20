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


def add_hosting_service(user: User, type: str, base_url: str, config: dict):
    logger.info(f"creating {type} - {base_url}")
    hosting_service = HostingService.query.filter_by(
        user_id=user.id, type=type, base_url=base_url
    ).first()
    if hosting_service:
        logger.info(f"found {type} - {base_url}")
        return hosting_service

    hosting_service = HostingService()
    hosting_service.user = user
    hosting_service.type = type
    hosting_service.base_url = base_url
    hosting_service.config = json.dumps(config)
    return hosting_service


@cli_bp.cli.command()
def init():
    admin_email = os.environ["HUBGREP_ADMIN_EMAIL"]
    admin_password = os.environ["HUBGREP_ADMIN_PASSWORD"]

    admin = create_admin(admin_email, admin_password)

    admin_role = security.datastore.find_or_create_role("admin", permissions=["admin"])

    security.datastore.add_role_to_user(admin, admin_role)

    db.session.commit()

    hosting_services = [
        dict(type="github", base_url="https://api.github.com/", config=dict())
    ]

    for hosting_service in hosting_services:
        s = add_hosting_service(admin, **hosting_service)
        db.session.add(s)
    db.session.commit()
