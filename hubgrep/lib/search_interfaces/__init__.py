import json
from requests_cache.core import CachedSession
from requests_cache.backends.redis import RedisCache
from flask import current_app as app


from hubgrep.lib.search_interfaces.github import GitHubSearch
from hubgrep.lib.search_interfaces.gitea import GiteaSearch
from hubgrep.lib.search_interfaces.gitlab import GitLabSearch
from hubgrep import redis_client

search_interfaces_by_name = dict(
    github=GitHubSearch, 
    gitlab=GitLabSearch, 
    gitea=GiteaSearch
)



def get_search_interfaces(cache=False):
    search_interfaces = {}
    for name_bytes in redis_client.keys('hosting_service:*'):
        name = name_bytes.decode()
        config_str = redis_client.get(name)
        config = json.loads(config_str)

        SearchClass = search_interfaces_by_name[config['type']]
        
        if cache:
            cache_backend = RedisCache(connection=redis_client)
            cached_session = CachedSession(expire_after=app.config['CACHE_TIME'], backend=cache_backend)
            args = {**config["args"], 'requests_session': cached_session}
        else:
            args = config['args']

        search_interfaces[name] = SearchClass(**args)
    print(search_interfaces)
    return search_interfaces

