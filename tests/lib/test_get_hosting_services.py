
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces
from hubgrep.models import HostingService



class TestGetHostingServices():


    def test_get_hosting_services(self, test_app):
        with test_app.app_context():
            hosting_services = get_hosting_service_interfaces(cache=False)
            print(hosting_services)

