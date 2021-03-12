import json
from requests_cache.core import CachedSession
from requests_cache.backends.redis import RedisCache
from flask import current_app as app


from hubgrep.lib.hosting_service_interfaces.github import GitHubSearch
from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch
from hubgrep.lib.hosting_service_interfaces.gitlab import GitLabSearch
from hubgrep import redis_client

hosting_service_interfaces_by_name = dict(
    github=GitHubSearch, gitlab=GitLabSearch, gitea=GiteaSearch
)


def get_hosting_service_interfaces(cache=False):
    hosting_service_interfaces = {}
    for name_bytes in redis_client.keys("hosting_service:*"):
        name = name_bytes.decode()
        config_str = redis_client.get(name)
        config = json.loads(config_str)

        SearchClass = hosting_service_interfaces_by_name[config["type"]]

        if cache:
            cache_backend = RedisCache(connection=redis_client)
            cached_session = CachedSession(
                expire_after=app.config["CACHE_TIME"], backend=cache_backend
            )
            args = {**config["args"], "requests_session": cached_session}
        else:
            args = config["args"]

        hosting_service_interfaces[name] = SearchClass(**args)
    print(hosting_service_interfaces)
    return hosting_service_interfaces
