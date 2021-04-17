
from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import HostingServiceInterface



class TestHostingServiceInterface():
    def test_set_headers(self, test_app):
        with test_app.app_context():
            base_hosting_service_interface = HostingServiceInterface("host_service_id", "base_url", "search_path", timeout=2)
            headers = base_hosting_service_interface.requests.headers
            assert 'referer' in headers.keys()
            assert headers['referer'].startswith("HubGrep v")


