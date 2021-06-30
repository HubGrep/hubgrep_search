
import click
from hubgrep.cli_blueprint import cli_bp
import os
import time
from flask import current_app
from hubgrep.models import HostingService, Repository
from hubgrep import security
from hubgrep import db
import urllib.parse
import shutil
import requests

def add_hoster(hoster_dict: dict):
    hoster_name = hoster_dict['hoster_name']
    hosting_service = HostingService.get(label=hoster_name)
    if not hosting_service:
        hosting_service = HostingService()
        hosting_service.label = hoster_name
        hosting_service.api_url = hoster_dict['api_url']
        hosting_service.landingpage_url = hoster_dict['landingpage_url']
        hosting_service.type = hoster_dict['type']


@cli_bp.cli.command(help="import repo data")
def import_repos():
    db.engine.dialect.psycopg2_batch_mode = True
    indexer_url = current_app.config['INDEXER']
    hosters_url = urllib.parse.urljoin(indexer_url, 'hosters')
    response = requests.get(hosters_url)
    hosters = response.json()

    for hoster_dict in hosters:
        hoster = add_hoster(**hoster_dict)
        create_instance_data(hoster)
