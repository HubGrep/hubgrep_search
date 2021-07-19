"""
Hosting-service interface and result-class for Gitea.
"""

import logging
from typing import List, Dict
from collections import OrderedDict

from flask import current_app
import pymysql.cursors

from urllib.parse import urljoin

from hubgrep.models import Repository

logger = logging.getLogger(__name__)


class SearchResult:
    def __init__(self, repo: Repository, weight: float):
        self.hosting_service_type = repo.hosting_service.type
        self.name = repo.name
        self.username = repo.username
        self.description = repo.description
        self.created_at = repo.created_at
        self.updated_at = repo.updated_at
        self.pushed_at = repo.pushed_at
        self.stars_count = repo.stars_count
        self.forks_count = repo.forks_count

        self.is_fork = repo.is_fork
        self.is_archived = repo.is_archived
        self.is_disabled = repo.is_disabled
        self.is_mirror = repo.is_mirror
        self.homepage_url = repo.homepage_url
        self.repo_url = repo.repo_url
        self.weight = weight

    def __repr__(self):
        return f"{self.username}/{self.name} ({self.weight})"


class SphinxSearch:
    """Interface for searching via Sphinx."""

    name = "Sphinx"

    @classmethod
    def _search_sphinx(cls, search_phrase) -> Dict[int, Dict]:
        connection = pymysql.connect(
            host=current_app.config["SPHINX_HOST"],
            port=9306,
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection:
            with connection.cursor() as cursor:
                sql = """
                    select id, weight() as weight
                    from repos
                    where match(%s) and is_archived = 0
                    order by weight desc
                    limit 1000
                    option
                        ranker=sph04,
                        field_weights=(repo_name=50, description=20)
                    """
                cursor.execute(sql, (search_phrase))
                logger.info(cursor.mogrify(sql, (search_phrase)))
                result_dicts = cursor.fetchall()

        logger.debug(f"found {len(result_dicts)} ids")
        search_results_by_id = OrderedDict()
        for result_dict in result_dicts:
            search_results_by_id[result_dict["id"]] = {
                    "weight": result_dict["weight"],
                }
        return search_results_by_id

    @classmethod
    def _get_from_db(cls, ids: List[int]) -> List[Repository]:
        repos = Repository.query.filter(Repository.id.in_(ids)).all()
        return repos

    @classmethod
    def search(
        cls, search_phrase: str, tags: dict = {}, context=None, **kwargs
    ) -> List[SearchResult]:

        sphinx_results = cls._search_sphinx(search_phrase)

        db_results = cls._get_from_db(sphinx_results.keys())

        # transform to "SearchResult" for frontend, adding result weights
        search_results = []
        for result in db_results:
            weight = sphinx_results[result.id]["weight"]
            search_result = SearchResult(
                result, weight
            )
            search_results.append(search_result)
        return search_results

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return urljoin(landingpage_url, "/api/v1/")
