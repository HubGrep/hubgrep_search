"""
Get registered hosting-service interfaces on this HubGrep instance.
"""

import logging
import requests

from typing import TYPE_CHECKING, Dict
from flask import current_app as app

from hubgrep.lib.cached_session.caches.no_cache import NoCache
from hubgrep.lib.cached_session.caches.redis_cache import RedisCache
from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.models import HostingService

if TYPE_CHECKING:
    from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
        HostingServiceInterface,
    )

logger = logging.getLogger(__name__)


class UnknownBackendException(Exception):
    pass


def _get_cache_backend():
    cache_backend_str = app.config["CACHE_BACKEND"]
    if cache_backend_str == None or cache_backend_str.lower() == "none":
        cache_backend = NoCache()

    elif cache_backend_str == "redis":
        redis_url = app.config["REDIS_URL"]
        cache_backend = RedisCache(
            redis_url=redis_url, expire_after=app.config["CACHE_TIME"]
        )

    else:
        raise UnknownBackendException(f'unknown cache backend "{cache_backend_str}"!')
    return cache_backend


def get_hosting_service_interfaces() -> Dict[str, "HostingServiceInterface"]:
    """Get registered hosting-service interfaces using the current cache-session."""
    hosting_service_interfaces = {}

    cache_backend = _get_cache_backend()
    logger.debug(f"using cache backend: {cache_backend}")
    for service in app.config["CACHED_HOSTING_SERVICES"]:
        service: HostingService
        if not service.has_local_index:
            cached_session = CachedSession(
                session=requests.Session(), cache=cache_backend
            )

            timeout = app.config["HOSTING_SERVICE_REQUEST_TIMEOUT"]

            hosting_service_interface = service.get_hosting_service_interface(
                cached_session, timeout
            )
            hosting_service_interfaces[service.api_url] = hosting_service_interface
        else:
            logger.debug(f"hoster {service.label} has local index")
        """
        # add sphinx as a "hoster" for search
        cached_session = CachedSession(session=requests.Session(), cache=cache_backend)

        timeout = app.config["HOSTING_SERVICE_REQUEST_TIMEOUT"]
        hosting_service_interface = SphinxSearch(
            host_service_id=None,
            api_url="sphinx",
            label="sphinx",
            config_dict={},
            cached_session=cached_session,
            timeout=app.config["HOSTING_SERVICE_REQUEST_TIMEOUT"],
        )
        hosting_service_interfaces[service.api_url] = hosting_service_interface
        """
    return hosting_service_interfaces
