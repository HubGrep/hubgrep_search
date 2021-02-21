from concurrent import futures
from typing import List

from hubgrep_meta.lib.search_interfaces._search_interface import (
    SearchInterface,
    SearchResult,
)

# todo: add sorting
# https://stackoverflow.com/questions/17903706/how-to-sort-list-of-strings-by-best-match-difflib-ratio

def fetch_concurrently(keywords, search_interfaces: List[SearchInterface]):
    # maybe as much executors as interfaces?
    with futures.ThreadPoolExecutor(max_workers=20) as executor:
        to_do = []
        for search_interface in search_interfaces:
            future = executor.submit(search_interface.search, keywords)
            to_do.append(future)

        results = []
        errors = []
        for future in futures.as_completed(to_do):
            success, base_url, result = future.result(timeout=5)
            if success:
                results += result
            else:
                errors.append((base_url, result))
        return results, errors
