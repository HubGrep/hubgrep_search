
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces

class TestGetHostingServices():

    def test_get_hosting_services(self, test_app):
        with test_app.app_context():
            hosting_services = get_hosting_service_interfaces(cache=False)
            test_hoster = list(hosting_services.values())[0]
            assert test_hoster.name == 'Gitea'

