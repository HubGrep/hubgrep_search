from unittest.mock import Mock

from hubgrep.lib.hosting_service_interfaces.github import (
    GitHubSearch,
    GitHubSearchResult,
)

# nice examples for requests mocking:
# https://realpython.com/python-mock-library/


class TestGithub:
    def get_mocked_response(self):
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.ok = True
        response_mock.json.return_value = dict(
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
        return response_mock

    def test_search(self, test_app):
        with test_app.app_context():
            github_search = GitHubSearch(
                "host_service_id",
                "api_url",
                timeout=2
            )
            github_search.requests = Mock()
            github_search.requests.get.return_value = self.get_mocked_response()

            success, api_url, results_or_error = github_search.search("")

            if not success:
                raise results_or_error

            results = results_or_error
            result: GitHubSearchResult = results[0]

            assert success is True
            assert api_url == "api_url"
            assert result.repo_name == "name"
            assert result.created_at_dt.timestamp() == 0
