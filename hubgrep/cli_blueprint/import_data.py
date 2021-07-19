import gzip
import tempfile
from hubgrep.cli_blueprint import cli_bp

import time
from flask import current_app
from hubgrep.models import HostingService
from hubgrep import db
import urllib.parse
import requests
import logging

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


def fetch_hoster_repos(export_url, hoster):
    logger.info(f"fetching {export_url}, {hoster}")

    table_name = "repositories"
    with tempfile.TemporaryFile(mode="w+b") as f:
        r = requests.get(export_url, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)

        logger.info(f"done fetching! ({f.tell()}b)")

        # set filepointer to beginning
        f.seek(0)
        with gzip.GzipFile(fileobj=f) as gz_file:
            con = db.engine.raw_connection()
            try:
                cur = con.cursor()
                # import the new data
                # this still lacks the hosting_service id, and we default to imported=false
                import_sql = f"""
                copy {table_name} (
                        foreign_id,
                        name,
                        username,
                        description,
                        created_at,
                        updated_at,
                        pushed_at,
                        stars_count,
                        forks_count,
                        is_private,
                        is_fork,
                        is_archived,
                        is_disabled,
                        is_mirror,
                        homepage_url,
                        repo_url
                        ) 
                FROM STDIN DELIMITER ';' CSV HEADER
                """
                cur.copy_expert(import_sql, gz_file)
                # cleanup the old repos:
                # we delete everything for this hoster that has imported=true
                cur.execute(
                    f"""
                            delete
                            from {table_name}
                            where
                                imported is true
                                and
                                hosting_service_id = %s
                            """,
                    (hoster.id,),
                )
                # set our new imports to "imported", and add the hoster id
                cur.execute(
                    f"""
                            update {table_name}
                            set
                                imported = true,
                                hosting_service_id = %s
                            where
                                imported is null
                            """,
                    (hoster.id,),
                )
                # commit!
                con.commit()
            finally:
                con.close()
        logger.info("imported table")


@cli_bp.cli.command(help="import the latest exports from the indexer")
def import_repos():
    """
    import all indexer exports,
    delete the old repo data afterwards
    """
    db.engine.dialect.psycopg2_batch_mode = True
    indexer_url = current_app.config["INDEXER"]
    hosters_url = urllib.parse.urljoin(indexer_url, "api/v1/hosters")
    response = requests.get(hosters_url)
    hosters = response.json()

    for hoster_dict in hosters:
        hoster = add_hoster(hoster_dict)
        exports = hoster_dict.get("exports_unified")
        if exports:
            export_url = exports[0]["url"]
            before = time.time()
            fetch_hoster_repos(export_url, hoster)
            logger.info(f"import took {time.time() - before}s")
