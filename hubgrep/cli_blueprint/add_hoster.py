import os
import click
import json
from hubgrep.cli_blueprint import cli_bp

from hubgrep import db, security
from hubgrep.models import HostingService

@cli_bp.cli.command()
@click.argument("type", type=click.STRING)
@click.argument("api_url", type=click.STRING)
@click.argument("landingpage_url", type=click.STRING)
@click.argument("config", type=click.STRING)
def add_hoster(type, api_url, landingpage_url, config):
    admin_email = os.environ["HUBGREP_ADMIN_EMAIL"]
    admin = security.datastore.find_user(email=admin_email)
    if not admin:
        print('admin user not found. set the HUBGREP_ADMIN_EMAIL envvar and run "flask cli init"!')
        exit(0)

    h = HostingService()
    h.user_id = admin.id
    h.type = type

    # todo: validate
    h.api_url = api_url
    h.landingpage_url = landingpage_url
    h.config = config
    h.set_service_label()

    print(f"adding {h.api_url}")

    db.session.add(h)
    db.session.commit()



