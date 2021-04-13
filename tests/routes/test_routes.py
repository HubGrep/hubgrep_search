from flask.testing import FlaskClient


class TestRoutes:

    def test_search(self, test_client: FlaskClient):
        res = test_client.get('/')
        assert res.status_code == 200

    def test_localization_de(self, test_client: FlaskClient):
        res = test_client.get('/', headers=[("Accept-Language", "de")])
        html_attr = str(res.data).split("<html")[1].split(">")[0]
        assert 'lang="de"' in html_attr

    def test_about(self, test_client: FlaskClient):
        res = test_client.get('/about')
        assert res.status_code == 200
