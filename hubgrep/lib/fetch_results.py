import difflib
from concurrent import futures
from typing import List

from hubgrep.lib.search_interfaces._search_interface import (
    SearchInterface,
    SearchResult,
)


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


def fetch_concurrently(keywords, search_interfaces: List[SearchInterface]):
    # maybe as much executors as interfaces?
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do = []
        for name, search_interface in search_interfaces.items():
            future = executor.submit(search_interface.search, keywords)
            to_do.append(future)

        results = []
        errors = []
        for future in futures.as_completed(to_do):
            success, base_url, _results = future.result(timeout=50)
            if success:
                if _results:
                    _normalize(_results)
                    results += _results
            else:
                errors.append((base_url, _results))

        results = final_sort(keywords, results)
        return results, errors

def filter_results(results: List, include_archived=True, include_fork=True):
    if not include_archived:
        results = [r for r in results if r.is_archived is not True]
    if not include_fork:
        results = [r for r in results if r.is_fork is not True]
    return results
