from flask.testing import FlaskClient


class TestRoutes:

    def test_search(self, test_client: FlaskClient):
        res = test_client.get('/')
        assert res.status_code == 200

    def test_localization_de(self, test_client: FlaskClient):
        res = test_client.get('/', headers=[("Accept-Language", "de")])
        assert '<html lang="de">' in str(res.data)

    def test_about(self, test_client: FlaskClient):
        res = test_client.get('/about')
        assert res.status_code == 200
