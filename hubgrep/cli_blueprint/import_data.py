import gzip
import tempfile
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
import json
import datetime

class DateTimeDecoder(json.JSONDecoder):
    """
    json encoder that can dump datetimes
    """
    pass


def add_hoster(hoster_dict: dict):
    hoster_name = hoster_dict['hoster_name']
    hosting_service = HostingService.query.filter_by(label=hoster_name).first()
    if not hosting_service:
        hosting_service = HostingService()

    hosting_service.label = hoster_name
    hosting_service.api_url = hoster_dict['api_url']
    hosting_service.landingpage_url = hoster_dict['landingpage_url']
    hosting_service.type = hoster_dict['type']
    hosting_service.has_local_index = True
    db.session.add(hosting_service)
    db.session.commit()
    return hosting_service

def fetch_hoster_repos(export_url):
    with tempfile.TemporaryFile(mode='wb') as f:

        r = requests.get(export_url, stream=True)
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

        f.seek(0)
        gz_file = gzip.GzipFile(fileobj=f, mode='rb')
        import ijson

        parser = ijson.parse(gz_file)
        for prefix, key, value in parser:
            print(prefix, key, value)


@cli_bp.cli.command(help="import repo data")
def import_repos():
    db.engine.dialect.psycopg2_batch_mode = True
    indexer_url = current_app.config['INDEXER']
    hosters_url = urllib.parse.urljoin(indexer_url, 'api/v1/hosters')
    response = requests.get(hosters_url)
    print(response.text)
    hosters = response.json()

    for hoster_dict in hosters:
        hoster = add_hoster(hoster_dict)
        export_url = hoster_dict['latest_export_json_gz']
        type = hoster_dict['type']






