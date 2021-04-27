from unittest.mock import Mock

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import HostingServiceInterfaceResult
from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch, GiteaSearchResult

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

    def test_search(self, test_app, cached_session):
        with test_app.app_context():
            gitea_search = GiteaSearch(
                "host_service_id", "api_url", "a label", dict(), cached_session=cached_session, timeout=2
            )
            gitea_search.cached_session.get = Mock()
            gitea_search.cached_session.get.return_value = self.get_cached_response()

            interface_result = gitea_search.search("")

            if not interface_result.response.success:
                raise Exception(interface_result.response.error_msg)

            result = interface_result.search_results[0]

            assert interface_result.response.success is True
            assert interface_result.response.url == "api_url"
            assert result.repo_name == "name"
            assert result.created_at_dt.timestamp() == 0
