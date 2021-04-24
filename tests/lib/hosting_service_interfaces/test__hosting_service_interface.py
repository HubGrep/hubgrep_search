import requests

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
)

from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.lib.cached_session.caches.no_cache import NoCache


class TestHostingServiceInterface:
    def test_set_headers(self, test_app):
        with test_app.app_context():
            cached_session = CachedSession(session=requests.Session(), cache=NoCache())
            base_hosting_service_interface = HostingServiceInterface(
                "host_service_id",
                "base_url",
                "search_path",
                cached_session=cached_session,
                timeout=2,
            )
            headers = base_hosting_service_interface.requests.headers
            assert "referer" in headers.keys()
            assert headers["referer"].startswith("HubGrep v")
