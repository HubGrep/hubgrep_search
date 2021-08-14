import click
from hubgrep.cli_blueprint import cli_bp

from hubgrep import db
from hubgrep.models import HostingService


@cli_bp.cli.command()
@click.argument("type", type=click.STRING)
@click.argument("api_url", type=click.STRING)
@click.argument("landingpage_url", type=click.STRING)
@click.argument("config", type=click.STRING)
def add_hoster(type, api_url, landingpage_url, config):
    h = HostingService()
    h.type = type

    # todo: validate
    h.api_url = api_url
    h.landingpage_url = landingpage_url
    h.config = config

    print(f"adding {h.api_url}")

    db.session.add(h)
    db.session.commit()

