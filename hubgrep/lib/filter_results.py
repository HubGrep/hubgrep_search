""" Filter search results. """

from typing import TYPE_CHECKING
from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import SearchResult

if TYPE_CHECKING:
    from hubgrep.frontend_blueprint.routes.search import SearchForm


def _filter_by_date(item: SearchResult, form: "SearchForm") -> bool:
    """ Filter results based on time against cutoffs defined in hubgrep.lib.search_form. """
    return (
            (not form.created_after_dt or item.created_at_dt > form.created_after_dt) and
            (not form.created_before_dt or item.created_at_dt < form.created_before_dt) and
            (not form.updated_after_dt or item.last_commit_dt > form.updated_after_dt)
    )


def filter_results(results: [SearchResult], form: "SearchForm") -> [SearchResult]:
    """ Filter results by properties defined in hubgrep.lib.search_form. """
    def predicate(item: SearchResult):
        return (
                not (
                        (form.exclude_forks and item.is_fork) or  # filter forks
                        (form.exclude_archived and item.is_archived)  # filter archived
                )
                and not form.exclude_service_checkboxes[item.host_service_id].is_checked  # filter on hosting-services
                and _filter_by_date(item, form)  # filters based on time
        )

    return list(filter(predicate, results))
