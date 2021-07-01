"""
Hosting-service interface and result-class for Gitea.
"""

import logging
from typing import List

from flask import current_app
import pymysql.cursors


from urllib.parse import urljoin
from iso8601 import iso8601


from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    HostingServiceInterfaceResponse,
    SearchResult,
)

from hubgrep.models import Repository

logger = logging.getLogger(__name__)


class SphinxSearchResult(SearchResult):
    def __init__(self, search_result_item: Repository, host_service_id):
        repo_name = search_result_item.name
        owner_name = search_result_item.namespace
        repo_description = search_result_item.description
        last_commit_dt = search_result_item.updated_at
        created_at_dt = search_result_item.created_at
        language = search_result_item.language
        license = search_result_item.license_name

        stars = search_result_item.stars_count
        forks = search_result_item.forks_count
        is_fork = search_result_item.is_fork
        is_archived = search_result_item.is_archived
        html_url = search_result_item.html_url

        super().__init__(
            host_service_id=host_service_id,
            repo_name=repo_name,
            repo_description=repo_description,
            html_url=html_url,
            owner_name=owner_name,
            last_commit_dt=last_commit_dt,
            created_at_dt=created_at_dt,
            language=language,
            license=license,
            forks=forks,
            stars=stars,
            is_fork=is_fork,
            is_archived=is_archived,
        )


class FakeResponse:
    success = True


class SphinxSearch(HostingServiceInterface):
    """ Interface for searching via Sphinx. """

    name = "Sphinx"

    def __init__(
        self,
        host_service_id,
        api_url,
        label,
        config_dict,
        cached_session,
        timeout=None,
    ):
        super().__init__(
            host_service_id=host_service_id,
            api_url=api_url,
            search_path="repos/search",
            label=label,
            api_key=None,
            cached_session=cached_session,
            timeout=timeout,
        )

    def search_sphinx(self, keywords):
        connection = pymysql.connect(
            host="sphinx",
            port=9306,
            cursorclass=pymysql.cursors.DictCursor,
        )

        with connection:
            with connection.cursor() as cursor:
                sql = "select * from repos where match(%s) limit 1000"
                cursor.execute(sql, (" ".join(keywords)))
                result_dicts = cursor.fetchall()
        result_ids = [d["id"] for d in result_dicts]
        return result_ids

    def get_from_db(self, ids: List[int]):
        repos = Repository.query.filter(Repository.id.in_(ids)).all()
        results = [SphinxSearchResult(repo, self.host_service_id) for repo in repos]
        return results

    def _search(
        self, keywords: list = [], tags: dict = {}, context=None, **kwargs
    ) -> HostingServiceInterfaceResponse:
        ids = self.search_sphinx(keywords)
        with context:
            results = self.get_from_db(ids)
        return HostingServiceInterfaceResponse(self, FakeResponse, results)

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return urljoin(landingpage_url, "/api/v1/")
