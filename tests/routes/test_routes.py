import unittest

from flask.testing import FlaskClient

from hubgrep import create_app


class TestRoutes(unittest.TestCase):
    _test_client: FlaskClient = create_app().test_client()

    def test_index(self):
        res = self._test_client.get('/')
        assert res.status_code == 200

    def test_about(self):
        res = self._test_client.get('/about')
        assert res.status_code == 200
