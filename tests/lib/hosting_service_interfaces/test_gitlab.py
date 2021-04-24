import requests
from unittest.mock import Mock

from hubgrep.lib.hosting_service_interfaces.gitlab import (
    GitLabSearch,
    GitLabSearchResult,
)
from hubgrep.lib.cached_session.cached_response import CachedResponse

# nice examples for requests mocking:
# https://realpython.com/python-mock-library/


class TestGitlab:
    def get_cached_response(self):
        response_json = [
            dict(
                name="name",
                namespace=dict(path="owner_name"),
                repo_description="repo_description",
                last_activity_at="1970-01-01T00:00:00.000Z",
                created_at="1970-01-01T00:00:00.000Z",
                star_count=-1,
                forks_count=-1,
                http_url_to_repo="html_url",
            ),
        ]
        cached_response = CachedResponse(
            url="api_url",
            success=True,
            status_code=200,
            response_json=response_json,
            error_msg="",
        )
        return cached_response

    def test_search(self, test_app, cached_session):
        with test_app.app_context():
            gitlab_search = GitLabSearch(
                "host_service_id",
                "api_url",
                "api_token",
                cached_session=cached_session,
                timeout=2,
            )
            gitlab_search.cached_session = Mock()
            gitlab_search.cached_session.get.return_value = self.get_cached_response()

            cached_response, results = gitlab_search.search("")

            if not cached_response.success:
                raise cached_response.error_msg

            result: GitLabSearchResult = results[0]

            assert cached_response.success is True
            assert cached_response.url == "api_url"
            assert result.repo_name == "name"
            assert result.created_at_dt.timestamp() == 0
