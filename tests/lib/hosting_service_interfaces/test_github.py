import requests
from unittest.mock import Mock

from hubgrep.lib.hosting_service_interfaces.github import (
    GitHubSearch,
    GitHubSearchResult,
)
from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.lib.cached_session.caches.no_cache import NoCache
from hubgrep.lib.cached_session.cached_response import CachedResponse

# nice examples for requests mocking:
# https://realpython.com/python-mock-library/


class TestGithub:
    def get_cached_response(self):
        response_json = dict(
            items=[
                dict(
                    name="name",
                    owner=dict(login="owner_name"),
                    description="repo_description",
                    updated_at="1970-01-01T00:00:00.000Z",
                    created_at="1970-01-01T00:00:00.000Z",
                    language="language",
                    licence=dict(name="license"),
                    stargazers_count=-1,
                    forks_count=-1,
                    fork=True,
                    html_url="html_url",
                ),
            ]
        )

        cached_response = CachedResponse(
            url="api_url",
            success=True,
            status_code=200,
            response_json=response_json,
            error_msg="",
        )
        return cached_response

    def test_search(self, test_app):
        with test_app.app_context():
            cached_session = CachedSession(session=requests.Session(), cache=NoCache())
            github_search = GitHubSearch(
                "host_service_id",
                "api_url",
                cached_session=cached_session,
                timeout=2
            )
            github_search.cached_session = Mock()
            github_search.cached_session.get.return_value = self.get_cached_response()

            cached_response, results = github_search.search("")

            if not cached_response.success:
                raise cached_response.error_msg

            result: GitHubSearchResult = results[0]

            assert cached_response.success is True
            assert cached_response.url == "api_url"
            assert result.repo_name == "name"
            assert result.created_at_dt.timestamp() == 0
