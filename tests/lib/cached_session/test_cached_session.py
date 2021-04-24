import pytest

from unittest.mock import Mock, patch

from hubgrep.lib.cached_session.caches.no_cache import NoCache
from hubgrep.lib.cached_session.caches.redis_cache import RedisCache
from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.lib.cached_session.cached_response import CachedResponse


class TestCachedSession:
    def test_make_key(self, cached_session: CachedSession):
        hash_1 = cached_session.make_key(
            "method", "url", *["arg"], **dict(kwarg="something")
        )
        hash_2 = cached_session.make_key(
            "method", "url", *["arg"], **dict(kwarg="something else")
        )
        _hash_1 = cached_session.make_key(
            "method", "url", *["arg"], **dict(kwarg="something")
        )

        assert _hash_1 == hash_1
        assert hash_1 != hash_2

    def get_cached_response(self):
        cached_response = CachedResponse(
            url="api_url",
            success=True,
            status_code=200,
            response_json=dict(some="thing"),
            error_msg="",
        )
        return cached_response

    def test_request_hit_cache(self, test_app, cached_session):
        cached_session.cache.get = Mock()
        cached_session.cache.get.return_value = self.get_cached_response().serialize()

        cached_session.session.request = Mock()

        cached_session.request("get", "url", *[], **{})

        # we should not have used session.request(), since the cache returned something
        assert not cached_session.session.request.called

    # we need to patch CachedResponse.from_response, so we can test if its called.
    # also, our request returns mocked nonsense and that would fail. :)
    @patch("hubgrep.lib.cached_session.cached_response.CachedResponse.from_response")
    def test_request_not_hit_cache(self, test_app, cached_session):
        cached_session.cache.get = Mock()
        cached_session.cache.get.return_value = None

        cached_session.session.request = Mock()
        cached_session.session.request.return_value = "nonsense"

        cached_session.request("get", "url", *[], **{})

        # we should have called session.get, since the cache didnt return anything
        assert cached_session.session.request.called
        assert CachedResponse.from_response.called
