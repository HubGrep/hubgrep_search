import os
import click
import json
from hubgrep.cli_blueprint import cli_bp

from hubgrep import redis_client
from hubgrep import db, security
from flask_security import hash_password

@cli_bp.cli.command()
def init():
    admin_email = os.environ['ADMIN_EMAIL']
    admin_password = os.environ['ADMIN_PASSWORD']

    admin = security.datastore.find_user(email=admin_email)
    if not admin:
        admin = security.datastore.create_user(email=admin_email, password=hash_password(admin_password))

    admin_role = security.datastore.find_or_create_role("admin", permissions=["admin"])
    security.datastore.add_role_to_user(admin, admin_role)

    db.session.commit()


