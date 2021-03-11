import os
from hubgrep.lib.search_interfaces import search_interfaces_by_name

# todo: these should live in a database

search_interface_config = {
    "github.com": dict(type="github", args=dict(base_url="https://api.github.com/")),
    "gitlab.org": dict(
        type="gitlab",
        args=dict(
            base_url="https://gitlab.com", api_token=os.environ["GITLAB_API_TOKEN"]
        ),
    ),  # new, empty user, read-only api
    "codeberg.org": dict(type="gitea", args=dict(base_url="https://codeberg.org")),
    "git.spip.net": dict(type="gitea", args=dict(base_url="https://git.spip.net")),
    "gitea.com": dict(type="gitea", args=dict(base_url="https://gitea.com")),
    "git.teknik.io": dict(type="gitea", args=dict(base_url="https://git.teknik.io")),
    "opendev.org": dict(type="gitea", args=dict(base_url="https://opendev.org")),
    "git.osuv.de": dict(type="gitea", args=dict(base_url="https://git.osuv.de")),
    "git.koehlerweb.org": dict(
        type="gitea", args=dict(base_url="https://git.koehlerweb.org")
    ),
    "gitea.vornet.cz": dict(
        type="gitea", args=dict(base_url="https://gitea.vornet.cz")
    ),
    "git.luehne.de": dict(type="gitea", args=dict(base_url="https://git.luehne.de")),
    "code.antopie.org": dict(
        type="gitea", args=dict(base_url="https://code.antopie.org")
    ),
    "git.daiko.fr": dict(type="gitea", args=dict(base_url="https://git.daiko.fr")),
    "gitea.anfuchs.de": dict(
        type="gitea", args=dict(base_url="https://gitea.anfuchs.de")
    ),
    "git.sablun.org": dict(type="gitea", args=dict(base_url="https://git.sablun.org")),
    "git.jcg.re": dict(type="gitea", args=dict(base_url="https://git.jcg.re")),
}


from requests_cache.core import CachedSession
from requests_cache.backends.redis import RedisCache
from redis import Redis


def get_search_interfaces(cache=False):
    search_interfaces = {}
    for name, config in search_interface_config.items():
        SearchClass = search_interfaces_by_name[config['type']]
        
        if cache:
            redis_connection = Redis('redis')
            cache_backend = RedisCache(connection=redis_connection)
            cached_session = CachedSession(expire_after=3600, backend=cache_backend)
            args = {**config["args"], 'requests_session': cached_session}
        else:
            args = config['args']

        search_interfaces[name] = SearchClass(**args)
    return search_interfaces

class Config:
    DEBUG = False
    TESTING = False
    LOGLEVEL = "debug"
    VERSION = "0.0.0"

    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"
    LANGUAGES = {"en": "English", "de": "Deutsch"}

    SEARCH_INTERFACES = get_search_interfaces(cache=True)


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
