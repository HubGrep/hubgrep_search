from iso8601 import iso8601

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    SearchResult,
)


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

    def __init__(self, search_result_item):
        repo_name = search_result_item["name"]
        owner_name = search_result_item["namespace"]["path"]
        repo_description = search_result_item.get("description", "?") or "?"
        last_commit = iso8601.parse_date(search_result_item["last_activity_at"])
        created_at = iso8601.parse_date(search_result_item["created_at"])
        language = ""
        license = ""

        stars = search_result_item["star_count"]
        forks = search_result_item["forks_count"]
        is_fork = None
        is_archived = None

        html_url = search_result_item["http_url_to_repo"]

        super().__init__(
            repo_name=repo_name,
            repo_description=repo_description,
            html_url=html_url,
            owner_name=owner_name,
            last_commit=last_commit,
            created_at=created_at,
            language=language,
            license=license,
            forks=forks,
            stars=stars,
            is_fork=is_fork,
            is_archived=is_archived,
        )


class GitLabSearch(HostingServiceInterface):
    name = "GitLab"

    def __init__(self, base_url, api_token, requests_session=None):
        super().__init__(
            base_url=base_url,
            search_path="/api/v4/search",
            requests_session=requests_session,
        )
        self.api_token = api_token

    def search(self, keywords: list = [], tags: dict = {}):
        tags = {**tags, **dict(scope="projects")}
        params = dict(search="+".join(keywords), **tags)
        try:
            response = self.requests.get(
                self.request_url,
                params=params,
                headers={"PRIVATE-TOKEN": self.api_token},
            )
        except Exception as e:
            return False, self.base_url, e

        result = response.json()
        results = [GitLabSearchResult(item) for item in result]
        return True, self.base_url, results
