from iso8601 import iso8601

from hubgrep.lib.search_interfaces._search_interface import (
    SearchResult,
    SearchInterface,
)


# https://developer.github.com/v3/search/


class GitHubSearchResult(SearchResult):
    """
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

    def __init__(self, search_result_item):
        repo_name = search_result_item["name"]
        owner_name = search_result_item["owner"]["login"]
        repo_description = search_result_item["description"] or "?"
        last_commit = iso8601.parse_date(search_result_item["updated_at"])
        created_at = iso8601.parse_date(search_result_item["created_at"])
        language = search_result_item["language"]
        license_dict = search_result_item.get("license")
        license = license_dict.get("name", None) if license_dict else None

        html_url = search_result_item["html_url"]

        super().__init__(
            repo_name=repo_name,
            repo_description=repo_description,
            html_url=html_url,
            owner_name=owner_name,
            last_commit=last_commit,
            created_at=created_at,
            language=language,
            license=license,
        )


class GitHubSearch(SearchInterface):
    name = "GitHub"

    # https://developer.github.com/v3/search/#search-repositories

    def __init__(self):
        super().__init__(
            base_url="https://api.github.com/", search_path="search/repositories"
        )

    def search(self, keywords: list = [], tags: dict = {}):
        params = dict(q="+".join(keywords), **tags)
        try:
            response = self.requests.get(self.request_url, params=params)

        except Exception as e:
            return False, self.base_url, e

        if not response.ok:
            return False, self.base_url, response.text

        result = response.json()

        results = [GitHubSearchResult(item) for item in result["items"]]
        return True, self.base_url, results
