from typing import List


def _filter_by_date(results: List, start, end):
    # TODO slice results
    return results


def _filter_by_service(results: List):
    return results


def filter_results(results: List, include_archived=True, include_fork=True):
    if not include_archived:
        results = [r for r in results if r.is_archived is not True]
    if not include_fork:
        results = [r for r in results if r.is_fork is not True]
    results = _filter_by_service(results)
    results = _filter_by_date(results)
    return results
