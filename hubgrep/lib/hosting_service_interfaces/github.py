"""
Hosting-service interface and result-class for Github.
"""

import logging

from iso8601 import iso8601

from typing import List, Union

from hubgrep.lib.cached_session.cached_response import CachedResponse
from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    SearchResult,
)

logger = logging.getLogger(__name__)


# https://developer.github.com/v3/search/


class GitHubSearchResult(SearchResult):
    """ GitHub search result - example response from Github API:
        {
      "id": 3081286,
      "node_id": "MDEwOlJlcG9zaXRvcnkzMDgxMjg2",
      "name": "Tetris",
      "full_name": "dtrupenn/Tetris",
      "owner": {
        "login": "dtrupenn",
        "id": 872147,
        "node_id": "MDQ6VXNlcjg3MjE0Nw==",
        "avatar_url": "https://secure.gravatar.com/avatar/e7956084e75f239de85d3a31bc172ace?d=https://a248.e.akamai.net/assets.github.com%2Fimages%2Fgravatars%2Fgravatar-user-420.png",
        "gravatar_id": "",
        "url": "https://api.github.com/users/dtrupenn",
        "received_events_url": "https://api.github.com/users/dtrupenn/received_events",
        "type": "User"
      },
      "private": false,
      "html_url": "https://github.com/dtrupenn/Tetris",
      "description": "A C implementation of Tetris using Pennsim through LC4",
      "fork": false,
      "url": "https://api.github.com/repos/dtrupenn/Tetris",
      "created_at": "2012-01-01T00:31:50Z",
      "updated_at": "2013-01-05T17:58:47Z",
      "pushed_at": "2012-01-01T00:37:02Z",
      "homepage": "",
      "size": 524,
      "stargazers_count": 1
      "watchers_count": 1,
      "language": "Assembly",
      "forks_count": 0,
      "open_issues_count": 0,
      "master_branch": "master",
      "default_branch": "master",
      "score": 1.0
    }
    """

    def __init__(self, search_result_item, host_service_id):
        repo_name = search_result_item["name"]
        owner_name = search_result_item["owner"]["login"]
        repo_description = search_result_item["description"] or ""
        last_commit_dt = iso8601.parse_date(search_result_item["updated_at"])
        created_at_dt = iso8601.parse_date(search_result_item["created_at"])
        language = search_result_item["language"]
        license_dict = search_result_item.get("license")
        license = license_dict.get("name", None) if license_dict else None

        stars = search_result_item["stargazers_count"]
        forks = search_result_item["forks_count"]
        is_fork = search_result_item["fork"]
        is_archived = None

        html_url = search_result_item["html_url"]

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


class GitHubSearch(HostingServiceInterface):
    """ Interface for searching via GitHub. """
    name = "GitHub"

    # https://developer.github.com/v3/search/#search-repositories

    def __init__(
        self,
        host_service_id,
        api_url,
        cached_session,
        timeout=None,
    ):
        super().__init__(
            host_service_id=host_service_id,
            api_url=api_url,
            search_path="search/repositories",
            cached_session=cached_session,
            timeout=timeout,
        )

    def _search(
        self, keywords: list = [], tags: dict = {}
    ) -> (CachedResponse, List[GitHubSearchResult]):

        params = dict(q="+".join(keywords), **tags)
        response_result = self.cached_session.get(
            self.request_url,
            params=params,
            timeout=self.timeout,
        )
        if response_result.success:
            results = [
                GitHubSearchResult(item, self.host_service_id)
                for item in response_result.response_json["items"]
            ]
        else:
            results = []
        return response_result, results

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return ""
