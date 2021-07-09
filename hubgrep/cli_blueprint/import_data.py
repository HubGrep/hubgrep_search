import ijson
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
import logging
from sqlalchemy import and_

logger = logging.getLogger(__name__)


class DateTimeDecoder(json.JSONDecoder):
    """
    json encoder that can dump datetimes
    """

    pass


def add_hoster(hoster_dict: dict):
    api_url = hoster_dict["api_url"]
    hosting_service = HostingService.query.filter_by(api_url=api_url).first()
    if not hosting_service:
        hosting_service = HostingService()

    hosting_service.label = api_url
    hosting_service.api_url = hoster_dict["api_url"]
    hosting_service.landingpage_url = hoster_dict["landingpage_url"]
    hosting_service.type = hoster_dict["type"]
    hosting_service.has_local_index = True
    db.session.add(hosting_service)
    db.session.commit()
    return hosting_service


def fetch_hoster_repos(export_url, hoster, import_timestamp):
    logger.info(f"fetching {export_url}, {hoster}, {import_timestamp}")
    with tempfile.TemporaryFile(mode="w+b") as f:
        r = requests.get(export_url, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

        logger.info(f"done fetching! ({f.tell()})")
        f.seek(0)

        # clean up: if we import the same export twice, we need to get rid of the old one first
        Repository.__table__.delete().where(
            and_(
                Repository.hosting_service_id == hoster.id,
                Repository.import_timestamp == import_timestamp,
            )
        )

        gz_file = gzip.GzipFile(fileobj=f)

        chunk_size = 0
        repos_to_add = []

        for repo in ijson.items(gz_file, 'item', multiple_values=True):
            chunk_size += 1
            r = Repository.from_dict(repo, hoster, import_timestamp)
            if r:
                repos_to_add.append(r)
            if chunk_size >= 10000:
                logger.info("commiting chunk...")
                before = time.time()
                db.session.bulk_save_objects(repos_to_add)
                db.session.commit()
                logger.info(f'took {time.time() - before}')
                chunk_size = 0
                repos_to_add = []
        
        logger.info("commiting last chunk...")
        db.session.bulk_save_objects(repos_to_add)
        db.session.commit()
        Repository.__table__.delete().where(
            and_(
                Repository.hosting_service_id == hoster.id,
                Repository.import_timestamp != import_timestamp,
            )
        )
        """
        # reading in chunks
        f.seek(0)
        gz_file = gzip.GzipFile(fileobj=f)
        import ijson

        parser = ijson.parse(gz_file)
        for prefix, key, value in parser:
            print(prefix, key, value)
        """


@cli_bp.cli.command(help="import repo data")
def import_repos():
    db.engine.dialect.psycopg2_batch_mode = True
    indexer_url = current_app.config["INDEXER"]
    hosters_url = urllib.parse.urljoin(indexer_url, "api/v1/export_hosters")
    response = requests.get(hosters_url)
    hosters = response.json()

    for hoster_dict in hosters:
        hoster = add_hoster(hoster_dict)
        exports = hoster_dict.get("exports")
        if exports:
            export_url = exports[0]["url"]
            import_timestamp = datetime.datetime.fromisoformat(
                exports[0]["created_at"]
            ).timestamp()
            fetch_hoster_repos(export_url, hoster, import_timestamp)
