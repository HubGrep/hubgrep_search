from hubgrep.models import HostingService


class TestHostingService:

    def test_service_domain(self, test_app):
        with test_app.app_context():

            hosting_service = HostingService()

            test_landingpage = 'https://landingpage.com/'
            expected_domain = 'landingpage.com'

            hosting_service.landingpage_url = test_landingpage
            hosting_service.api_url = 'something else'

            assert hosting_service.domain == expected_domain
