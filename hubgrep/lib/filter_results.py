from typing import TYPE_CHECKING
from hubgrep.lib.hosting_service_interfaces._hosting_service_interface import SearchResult

if TYPE_CHECKING:
    from hubgrep.frontend_blueprint.routes.index import SearchForm


def _filter_by_date(item: SearchResult, form: "SearchForm") -> bool:
    return (
        (form.created_after_dt is False or item.created_at_dt > form.created_after_dt) and
        (form.created_before_dt is False or item.created_at_dt < form.created_before_dt) and
        (form.updated_after_dt is False or item.last_commit_dt > form.updated_after_dt)
    )

def filter_results(results: [SearchResult], form: "SearchForm") -> [SearchResult]:
    def predicate(item: SearchResult):
        return (
                not (
                    (form.exclude_forks and item.is_fork) or                        # filter forks
                    (form.exclude_archived and item.is_archived)                    # filter archived
                ) and
                not form.exclude_service_checkboxes[item.host_service_id].is_checked and        # filter based on hosting-service
                _filter_by_date(item, form)                                         # filters based on time
        )

    return list(filter(predicate, results))
