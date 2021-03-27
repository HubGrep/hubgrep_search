import json
from requests_cache.core import CachedSession
from requests_cache.backends.redis import RedisCache
from flask import current_app as app


from hubgrep.lib.hosting_service_interfaces.github import GitHubSearch
from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch
from hubgrep.lib.hosting_service_interfaces.gitlab import GitLabSearch

from hubgrep.models import HostingService
from hubgrep import redis_client

hosting_service_interfaces_by_name = dict(
    github=GitHubSearch, gitlab=GitLabSearch, gitea=GiteaSearch
)


def get_hosting_service_interfaces(cache=False):
    hosting_service_interfaces = {}

    for service in HostingService.query.all():
        service: HostingService

        config_str = service.config
        config = json.loads(config_str)

        SearchClass = hosting_service_interfaces_by_name[service.type]

        if cache:
            cache_backend = RedisCache(connection=redis_client)
            cached_session = CachedSession(
                expire_after=app.config["CACHE_TIME"], backend=cache_backend
            )
            args = dict(
                api_url=service.api_url,
                **config,
                requests_session=cached_session,
            )
        else:
            args = dict(
                api_url=service.api_url,
                **config,
            )

        hosting_service_interfaces[service.api_url] = SearchClass(**args)
    return hosting_service_interfaces
