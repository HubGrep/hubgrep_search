import pytest
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces, _get_cache_backend, UnknownBackendException

class TestGetHostingServices():

    def test__get_cache_backend(self, test_app):
        with test_app.app_context():
            test_app.config['CACHE_BACKEND'] = 'NonE'
            backend = _get_cache_backend()
            assert backend is None

            test_app.config['CACHE_BACKEND'] = 'memory'
            backend = _get_cache_backend()
            assert backend == 'memory'

            test_app.config['CACHE_BACKEND'] = None
            backend = _get_cache_backend()
            assert backend is None

            test_app.config['CACHE_BACKEND'] = 'something undefined'
            with pytest.raises(UnknownBackendException):
                backend = _get_cache_backend()


    def test_get_hosting_services(self, test_app):
        with test_app.app_context():
            test_app.config['CACHE_BACKEND'] = 'memory'
            hosting_services = get_hosting_service_interfaces()
            test_hoster = list(hosting_services.values())[0]
            assert test_hoster.name == 'Gitea'

