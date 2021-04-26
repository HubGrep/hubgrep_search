import logging
from iso8601 import iso8601
from urllib.parse import urljoin

from typing import List, Union

from hubgrep.lib.cached_session.cached_response import CachedResponse
from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    SearchResult,
)

logger = logging.getLogger(__name__)


class GitLabSearchResult(SearchResult):
    """
    {
      "id": 6,
      "description": "Nobis sed ipsam vero quod cupiditate veritatis hic.",
      "name": "Flight",
      "name_with_namespace": "Twitter / Flight",
      "path": "flight",
      "path_with_namespace": "twitter/flight",
      "created_at": "2017-09-05T07:58:01.621Z",
      "default_branch": "master",
      "tag_list":[],
      "ssh_url_to_repo": "ssh://jarka@localhost:2222/twitter/flight.git",
      "http_url_to_repo": "http://localhost:3000/twitter/flight.git",
      "web_url": "http://localhost:3000/twitter/flight",
      "avatar_url": null,
      "star_count": 0,
      "forks_count": 0,
      "last_activity_at": "2018-01-31T09:56:30.902Z"
    }
    """

    def __init__(self, search_result_item, host_service_id):
        repo_name = search_result_item["name"]
        owner_name = search_result_item["namespace"]["path"]
        repo_description = search_result_item.get("description", "") or ""
        last_commit_dt = iso8601.parse_date(search_result_item["last_activity_at"])
        created_at_dt = iso8601.parse_date(search_result_item["created_at"])
        language = ""
        license = ""

        stars = search_result_item["star_count"]
        forks = search_result_item["forks_count"]
        is_fork = None
        is_archived = None

        html_url = search_result_item["http_url_to_repo"]

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


class GitLabSearch(HostingServiceInterface):
    name = "GitLab"

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
            label=label,
            search_path="search",
            cached_session=cached_session,
            timeout=timeout,
        )
        self.api_token = config_dict["api_token"]

    def _search(
        self, keywords: list = [], tags: dict = {}
    ) -> ("GitLabSearch", CachedResponse, List[GitLabSearchResult]):
        tags = {**tags, **dict(scope="projects")}
        params = dict(search="+".join(keywords), **tags)

        response_result = self.cached_session.get(
            self.request_url,
            params=params,
            headers={"PRIVATE-TOKEN": self.api_token},
            timeout=self.timeout,
        )
        if response_result.success:
            results = [
                GitLabSearchResult(item, self.host_service_id)
                for item in response_result.response_json
            ]
        else:
            results = []
        return self, response_result, results

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return urljoin(landingpage_url, "/api/v4/")
