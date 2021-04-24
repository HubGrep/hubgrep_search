import pytest

from unittest.mock import Mock, patch

from hubgrep.lib.cached_session.caches.no_cache import NoCache
from hubgrep.lib.cached_session.caches.redis_cache import RedisCache
from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.lib.cached_session.cached_response import CachedResponse


class TestCachedResponse:
    def test_serialize_deserialize(self):
        cached_response = CachedResponse(
            "url",
            "success",
            "status_code",
            dict(response_json_content="bla"),
            "error_msg",
        )
        serialized = cached_response.serialize()

        assert CachedResponse.from_serialized(serialized).url == "url"




