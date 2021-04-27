import logging
from iso8601 import iso8601
from urllib.parse import urljoin

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    HostingServiceInterfaceResponse,
    SearchResult,
)

logger = logging.getLogger(__name__)


# https://try.gitea.io/api/swagger#/repository/hubgrep_meta.lib


class GiteaSearchResult(SearchResult):
    """
    {
      "allow_merge_commits": true,
      "allow_rebase": true,
      "allow_rebase_explicit": true,
      "allow_squash_merge": true,
      "archived": true,
      "avatar_url": "string",
      "clone_url": "string",
      "created_at": "2020-06-19T14:42:45.957Z",
      "default_branch": "string",
      "description": "string",
      "empty": true,
      "external_tracker": {
        "external_tracker_format": "string",
        "external_tracker_style": "string",
        "external_tracker_url": "string"
      },
      "external_wiki": {
        "external_wiki_url": "string"
      },
      "fork": true,
      "forks_count": 0,
      "full_name": "string",
      "has_issues": true,
      "has_pull_requests": true,
      "has_wiki": true,
      "html_url": "string",
      "id": 0,
      "ignore_whitespace_conflicts": true,
      "internal": true,
      "internal_tracker": {
        "allow_only_contributors_to_track_time": true,
        "enable_issue_dependencies": true,
        "enable_time_tracker": true
      },
      "mirror": true,
      "name": "string",
      "open_issues_count": 0,
      "open_pr_counter": 0,
      "original_url": "string",
      "owner": {
        "avatar_url": "string",
        "created": "2020-06-19T14:42:45.957Z",
        "email": "user@example.com",
        "full_name": "string",
        "id": 0,
        "is_admin": true,
        "language": "string",
        "last_login": "2020-06-19T14:42:45.957Z",
        "login": "string"
      },
      "permissions": {
        "admin": true,
        "pull": true,
        "push": true
      },
      "private": true,
      "release_counter": 0,
      "size": 0,
      "ssh_url": "string",
      "stars_count": 0,
      "template": true,
      "updated_at": "2020-06-19T14:42:45.957Z",
      "watchers_count": 0,
      "website": "string"
    }
    """

    def __init__(self, search_result_item, host_service_id):
        repo_name = search_result_item["name"]
        owner_name = search_result_item["owner"]["login"]
        repo_description = search_result_item["description"] or ""
        last_commit_dt = iso8601.parse_date(search_result_item["updated_at"])
        created_at_dt = iso8601.parse_date(search_result_item["created_at"])
        language = ""
        license_dict = search_result_item.get("license")
        license = license_dict.get("name", None) if license_dict else None

        stars = search_result_item["stars_count"]
        forks = search_result_item["forks_count"]
        is_fork = search_result_item.get("fork", None)
        is_archived = search_result_item.get("archived", None)

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


class GiteaSearch(HostingServiceInterface):
    name = "Gitea"

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
            search_path="repos/search",
            cached_session=cached_session,
            timeout=timeout,
        )

    def _search(
        self, keywords: list = [], tags: dict = {}
    ) -> HostingServiceInterfaceResponse:

        params = dict(q="+".join(keywords), **tags)
        response = self.cached_session.get(
            self.request_url,
            params=params,
            headers=self._get_request_headers(),
            timeout=self.timeout,
        )

        if response.success:
            results = [
                GiteaSearchResult(item, self.host_service_id)
                for item in response.response_json["data"]
            ]
        else:
            results = []

        return HostingServiceInterfaceResponse(self, response, results)

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return urljoin(landingpage_url, "/api/v1/")
