import requests
from unittest.mock import Mock

from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch, GiteaSearchResult
from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.lib.cached_session.caches.no_cache import NoCache
from hubgrep.lib.cached_session.cached_response import CachedResponse

class TestGitea:
    def get_cached_response(self):
        response_json = dict(
            data=[
                dict(
                    name="name",
                    owner=dict(login="owner_login"),
                    description="repo_description",
                    updated_at="1970-01-01T00:00:00.000Z",
                    created_at="1970-01-01T00:00:00.000Z",
                    license=dict(name="licence_name"),
                    stars_count=-1,
                    forks_count=-1,
                    fork=True,
                    archived=True,
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
            gitea_search = GiteaSearch(
                "host_service_id", "api_url", cached_session=cached_session, timeout=2
            )
            gitea_search.cached_session.get = Mock()
            gitea_search.cached_session.get.return_value = self.get_cached_response()

            cached_response, results = gitea_search.search("")

            if not cached_response.success:
                raise cached_response.error_msg

            result: GiteaSearchResult = results[0]

            assert cached_response.success is True
            assert cached_response.url == "api_url"
            assert result.repo_name == "name"
            assert result.created_at_dt.timestamp() == 0
