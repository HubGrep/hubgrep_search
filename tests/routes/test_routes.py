from flask.testing import FlaskClient


class TestRoutes:

    def test_search(self, test_client: FlaskClient):
        res = test_client.get('/')
        assert res.status_code == 200

    def test_localization_de(self, test_client: FlaskClient):
        languages = [("de-DE", "de"), ("de", "de"), ("en", "en")]
        for lang in languages:
            res = test_client.get('/', headers=[("Accept-Language", lang[0])])
            html_attr = str(res.data).split("<html")[1].split(">")[0]
            assert 'lang="{}"'.format(lang[1]) in html_attr

    def test_about(self, test_client: FlaskClient):
        res = test_client.get('/about')
        assert res.status_code == 200
