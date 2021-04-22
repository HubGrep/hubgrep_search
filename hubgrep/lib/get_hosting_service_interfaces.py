import json
import logging

import redis

from requests_cache.core import CachedSession
from flask import current_app as app

from hubgrep.lib.hosting_service_interfaces.github import GitHubSearch
from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch
from hubgrep.lib.hosting_service_interfaces.gitlab import GitLabSearch
from hubgrep.models import HostingService

logger = logging.getLogger(__name__)


hosting_service_interfaces_by_name = dict(
    github=GitHubSearch, gitlab=GitLabSearch, gitea=GiteaSearch
)

class UnknownBackendException(Exception):
    pass

def _get_cache_backend():
    cache_backend_str = app.config['CACHE_BACKEND']
    if cache_backend_str == None or cache_backend_str.lower() == 'none':
        cache_backend = None

    elif cache_backend_str == 'redis':
        from requests_cache.backends import RedisCache

        redis_url = app.config['REDIS_URL']
        redis_client = redis.from_url(redis_url)
        cache_backend = RedisCache(connection=redis_client)

    elif cache_backend_str == 'memory':
        cache_backend = 'memory'

    else:
        raise UnknownBackendException(f'unknown cache backend "{cache_backend_str}"!')
    return cache_backend

def get_hosting_service_interfaces():
    hosting_service_interfaces = {}

    for service in app.config["CACHED_HOSTING_SERVICES"]:
        service: HostingService

        config_str = service.config
        config = json.loads(config_str)

        SearchClass = hosting_service_interfaces_by_name[service.type]
        cache_backend = _get_cache_backend()
        if cache_backend:
            logger.debug(f'using cache cache backend: {cache_backend}')
            session = CachedSession(
                expire_after=app.config["CACHE_TIME"], backend=cache_backend
            )
        else:
            session = None

        args = dict(
            host_service_id=service.id,
            api_url=service.api_url,
            **config,
            requests_session=session,
        )

        hosting_service_interfaces[service.api_url] = SearchClass(**args)
    return hosting_service_interfaces
