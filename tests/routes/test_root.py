import unittest

from flask.testing import FlaskClient

from crawler_api.flask_app import app


class TestRoot(unittest.TestCase):
    def test_root(self):
        client: FlaskClient = app.test_client()
        res = client.get('/')
        assert res.status_code == 200
