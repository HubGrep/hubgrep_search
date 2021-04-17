import logging
import difflib
from concurrent import futures
from typing import List

from flask import current_app as app

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    SearchResult,
)


logger = logging.getLogger(__name__)


def final_sort(keywords, results):
    """
    order results based on normalized score and best text match
    """
    # https://stackoverflow.com/questions/17903706/how-to-sort-list-of-strings-by-best-match-difflib-ratio
    def _key(result: SearchResult):
        key = result.repo_name + " " + result.repo_description
        ratio = difflib.SequenceMatcher(None, key, " ".join(keywords)).ratio()
        ratio = result.forks_normalized + ratio * 2
        result.score = ratio
        return ratio

    return sorted(results, key=_key, reverse=True)


def _normalize(results):
    """
    normalize fork count of the results of a service

    # todo: last commit, age, stars...?
    # what about a "group" of forks?
    # basically everything that is based on the same commit tree?
    # i think the most interesting one in that group is the most forked one
    # could we do that based on first commit id, or do we have to store a list of forks for everything?
    """
    max_value_result = max(results, key=lambda result: result.forks)
    for result in results:
        if max_value_result.forks > 0:
            result.forks_normalized = result.forks / max_value_result.forks
        else:
            # is this 0 or 1?
            result.forks_normalized = 0


def fetch_concurrently(keywords, hosting_service_interfaces: List[HostingServiceInterface]):
    # maybe as much executors as interfaces?
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do = []
        for name, hosting_service_interface in hosting_service_interfaces.items():
            future = executor.submit(hosting_service_interface.search, keywords)
            to_do.append(future)

        results = []
        errors = []

        future_timeout = app.config['HOSTER_SERVICE_REQUESTS_TIMEOUT'] + 2
        try:
            for future in futures.as_completed(to_do, timeout=future_timeout):
                success, base_url, _results = future.result()
                if success:
                    if _results:
                        _normalize(_results)
                        results += _results
                else:
                    errors.append((base_url, _results))
        except futures._base.TimeoutError as e:
            logger.error('something went wrong with the requests')
            logger.error(e, exc_info=True)
        if errors:
            logger.warn(f"got some errors: {errors}")
        results = final_sort(keywords, results)
        return results, errors
