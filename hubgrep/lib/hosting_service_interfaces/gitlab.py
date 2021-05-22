"""
Hosting-service interface and result-class for Gitlab.
"""

import logging
from iso8601 import iso8601
from urllib.parse import urljoin

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    HostingServiceInterfaceResponse,
    SearchResult,
)

logger = logging.getLogger(__name__)


class GitLabSearchResult(SearchResult):
    """ GitLab search result - example response from GitLab API:
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
    """ Interface for searching via GitLab. """
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
            config_dict=config_dict,
            search_path="search",
            cached_session=cached_session,
            timeout=timeout,
        )

    def _search(
            self, keywords: list = [], tags: dict = {}, **kwargs
    ) -> HostingServiceInterfaceResponse:
        tags = {**tags, **dict(scope="projects")}
        params = dict(search="+".join(keywords), **tags)

        response = self.cached_session.get(
            self.request_url,
            params=params,
            headers=self._get_request_headers(),
            timeout=self.timeout,
        )
        if response.success:
            results = [
                GitLabSearchResult(item, self.host_service_id)
                for item in response.response_json
            ]
        else:
            results = []
        return HostingServiceInterfaceResponse(self, response, results)

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return urljoin(landingpage_url, "/api/v4/")

    def _get_request_headers(self):
        headers = super()._get_request_headers()
        if "api_token" in self.config_dict.keys():
            headers["PRIVATE-TOKEN"] = self.config_dict["api_token"]
        else:
            logger.warning(
                f"setting GITLAB headers without PRIVATE-TOKEN - Config: {self.config_dict} - Headers: {headers}")
        return headers
