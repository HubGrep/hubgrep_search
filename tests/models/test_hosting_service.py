from hubgrep.models import HostingService


class TestHostingService:

    def test_set_service_label(self, test_app):
        with test_app.app_context():

            hosting_service = HostingService()

            test_landingpage = 'https://landingpage.com/'
            expected_label = 'landingpage.com'

            hosting_service.landingpage_url = test_landingpage
            hosting_service.api_url = 'something else'
            hosting_service.set_service_label()


            assert hosting_service.label == expected_label
