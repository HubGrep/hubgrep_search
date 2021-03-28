import logging
from typing import List, Union
from iso8601 import iso8601

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
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

    def __init__(self, host_service_id, api_url, requests_session=None):
        super().__init__(
            host_service_id=host_service_id,
            api_url=api_url,
            search_path="repos/search",
            requests_session=requests_session,
        )

    def search(
            self, keywords: list = [], tags: dict = {}
    ) -> (bool, str, Union[Exception, List[GiteaSearchResult]],):
        params = dict(q="+".join(keywords), **tags)
        try:
            response = self.requests.get(self.request_url, params=params)
            if not response.ok:
                return False, self.api_url, response.text
            result = response.json()
            results = [GiteaSearchResult(item, self.host_service_id) for item in result["data"]]
        except Exception as e:
            logger.error(result)
            logger.error(e, exc_info=True)
            return False, self.api_url, e
        return True, self.api_url, results
