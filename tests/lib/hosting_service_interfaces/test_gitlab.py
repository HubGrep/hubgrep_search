from unittest.mock import Mock

from hubgrep.lib.hosting_service_interfaces.gitlab import (
    GitLabSearch,
    GitLabSearchResult,
)

# nice examples for requests mocking:
# https://realpython.com/python-mock-library/


class TestGitlab:
    def get_mocked_response(self):
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.ok = True
        response_mock.json.return_value = [
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
        return response_mock

    def test_search(self, test_app):
        with test_app.app_context():
            gitlab_search = GitLabSearch("host_service_id", "api_url", "api_token")
            gitlab_search.requests = Mock()
            gitlab_search.requests.get.return_value = self.get_mocked_response()

            success, api_url, results_or_error = gitlab_search.search("")

            if not success:
                raise results_or_error

            results = results_or_error
            result: GitLabSearchResult = results[0]

            assert success is True
            assert api_url == "api_url"
            assert result.repo_name == "name"
            assert result.created_at_dt.timestamp() == 0
