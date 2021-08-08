import gzip
import tempfile
import time
import logging

import urllib.parse

import click
import requests

from flask import current_app

from hubgrep.models import HostingService
from hubgrep import db
from hubgrep.lib.table_helper import TableHelper
from hubgrep.cli_blueprint import cli_bp

logger = logging.getLogger(__name__)


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


def append_repos(gz_file, hoster, new_table_name):
    with TableHelper._cursor() as cursor:

        temp_table_name = "temp_repos"
        logger.info("creating temp table...")
        TableHelper.create_empty_temporary_repositories_table(cursor, temp_table_name)

        import_fields = [
            "foreign_id",
            "name",
            "username",
            "description",
            "created_at",
            "updated_at",
            "pushed_at",
            "stars_count",
            "forks_count",
            "is_private",
            "is_fork",
            "is_archived",
            "is_disabled",
            "is_mirror",
            "homepage_url",
            "repo_url",
        ]

        # import the new data to a temporary table
        # this still lacks the hosting_service id
        logger.info("starting import...")
        import_sql = f"""
        copy {temp_table_name} ({",".join(import_fields)})
        FROM STDIN DELIMITER ';' CSV HEADER
        """
        cursor.copy_expert(import_sql, gz_file)

        # count the new rows, because its nice to see
        cursor.execute(
            f"""
            select count(*) from {temp_table_name}
            """,
            (hoster.id,),
        )
        count = cursor.fetchone()
        logger.info(f"imported {count} repos for {hoster.api_url}")

        # append the new data to our actual table, setting the hoster id as we go
        logger.info("imported to temp table, importing to persistent table and setting hosting_service_id")
        cursor.execute(f"""
        INSERT INTO {new_table_name} ({",".join(import_fields)}, hosting_service_id)
        SELECT {",".join(import_fields)}, {hoster.id}
          FROM {temp_table_name};
          """
        )
        # table should automatically get dropped - but when? when we close the cursor..?
        logger.info("dropping temp table")
        TableHelper.drop_table(cursor, temp_table_name)


def fetch_hoster_repos(export_url, hoster, new_table_name):
    logger.info(f"fetching {export_url}, {hoster}")

    with tempfile.TemporaryFile(mode="w+b") as f:
        r = requests.get(export_url, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

        logger.info(f"done fetching! ({f.tell()}b)")

        # set filepointer to beginning
        f.seek(0)

        with gzip.GzipFile(fileobj=f) as gz_file:
            append_repos(gz_file, hoster, new_table_name)
        logger.info("imported table!")


def _get_tmp_table_name(identifier):
    return f"tmp_repositories_{identifier}"


@cli_bp.cli.command(help="import the latest exports from the indexer")
@click.argument("temp_table_name")
def import_repos(temp_table_name):
    """
    import all indexer exports to a new table,
    creates new HostingServices if neccessary
    """
    db.engine.dialect.psycopg2_batch_mode = True
    indexer_url = current_app.config["INDEXER_URL"]
    hosters_url = urllib.parse.urljoin(indexer_url, "api/v1/hosters")
    response = requests.get(hosters_url)
    hosters = response.json()

    with TableHelper._cursor() as cursor:
        # cleanup before we start
        TableHelper.drop_table(cursor, temp_table_name)
        # create new, empty table that looks like repositories
        TableHelper.create_empty_repositories_table(cursor, temp_table_name)

    for hoster_dict in hosters:
        hoster = add_hoster(hoster_dict)
        exports = hoster_dict.get("exports_unified")
        if exports:
            export_url = exports[0]["url"]
            before = time.time()
            fetch_hoster_repos(export_url, hoster, temp_table_name)
            logger.info(f"import took {time.time() - before}s")


@cli_bp.cli.command(help="delete old 'repositories' table, replace it with the new one")
@click.argument("temp_table_name")
def rotate_repositories_table(temp_table_name):
    logger.info("rotating tables...")
    with TableHelper._cursor() as cursor:
        table_to_replace = "repositories"
        table_with_new_data = temp_table_name
        TableHelper.rotate_tables(cursor, table_to_replace, table_with_new_data)
