import logging
import difflib
from concurrent import futures
from typing import List

from flask import current_app as app

from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import (
    HostingServiceInterface,
    HostingServiceInterfaceResult,
    SearchResult,
)

from hubgrep.lib.cached_session.cached_response import CachedResponse

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


def fetch_concurrently(
        keywords, hosting_service_interfaces: List[HostingServiceInterface]
) -> "AggregatedSearchResults":
    # maybe as much executors as interfaces?
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do = []
        for name, hosting_service_interface in hosting_service_interfaces.items():
            future = executor.submit(hosting_service_interface.search, keywords)
            to_do.append(future)

        results = []
        failed_responses = []

        # HOSTING_SERVICE_REQUEST_TIMEOUT is used in the hosting service classes.
        # its used as a limit to the first connect,
        # and then again for reading. (see https://docs.python-requests.org/en/master/user/advanced/#timeouts)
        # that means, the requests can take up to
        # two times the "HOSTING_SERVICE_REQUEST_TIMEOUT" time
        # before cancelling.
        # so we take this as a reference here, and add another second before
        # we actually break, throwing an error to the user
        future_timeout = (app.config["HOSTING_SERVICE_REQUEST_TIMEOUT"] * 2) + 1
        try:
            for future in futures.as_completed(to_do, timeout=future_timeout):
                interface_result = future.result()
                if interface_result.response.success:
                    if len(interface_result.search_results) > 0:
                        _normalize(interface_result.search_results)
                        results += interface_result.search_results
                else:
                    failed_responses.append(
                        FailedSearchResult(interface_result.hosting_service_interface, interface_result.response)
                    )
        except futures._base.TimeoutError as e:
            logger.error("something went wrong with the requests")
            logger.error(e, exc_info=True)
        if failed_responses:
            logger.warning(f"got some errors: {failed_responses}")
        results = final_sort(keywords, results)
        return AggregatedSearchResults(results, failed_responses)


class FailedSearchResult:
    hosting_service_interface: HostingServiceInterface
    response: CachedResponse

    def __init__(self, hosting_service_interface: HostingServiceInterface, response: CachedResponse):
        self.hosting_service_interface = hosting_service_interface
        self.response = response


class AggregatedSearchResults:
    search_results: List[SearchResult]
    failed_requests: List[FailedSearchResult]

    def __init__(self, search_results: List[SearchResult], failed_requests: List[FailedSearchResult]):
        self.search_results = search_results
        self.failed_requests = failed_requests
