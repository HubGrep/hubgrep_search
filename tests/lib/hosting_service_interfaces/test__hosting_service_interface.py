import unittest

from unittest import mock

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import HostingServiceInterface



class TestHostingServiceInterface():
    def test_set_headers(self, test_app):
        with test_app.app_context():
            base_hosting_service_interface = HostingServiceInterface("base_url", "search_path")
            headers = base_hosting_service_interface.requests.headers
            assert 'referer' in headers.keys()
            assert headers['referer'].startswith("HubGrep v")


