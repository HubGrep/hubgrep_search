""" Search page route. """

from flask import render_template
from flask import current_app as app
from flask import request

from hubgrep.constants import PARAM_OFFSET, PARAM_PER_PAGE
from hubgrep.lib.pagination import get_page_links
from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.filter_results import filter_results
from hubgrep.lib.hosting_service_interfaces.get_hosting_service_interfaces import get_hosting_service_interfaces
from hubgrep.lib.search_form import SearchForm
from hubgrep.frontend_blueprint import frontend

import logging

logger = logging.getLogger(__name__)

@frontend.route("/")
def search():
    results_paginated = []
    results_offset = int(request.args.get(PARAM_OFFSET, 0))
    results_per_page = int(request.args.get(PARAM_PER_PAGE, app.config['PAGINATION_PER_PAGE_DEFAULT']))
    form = SearchForm(search_phrase=request.args.get("s", ""),
                      exclude_service_checkboxes=SearchForm.get_request_service_checkboxes(),
                      exclude_forks=request.args.get("f", "") == "on",
                      exclude_archived=request.args.get("a", "") == "on",
                      created_after=request.args.get("ca", ""),
                      created_before=request.args.get("cb", ""),
                      updated_after=request.args.get("ua", ""))
    search_feedback = ""
    failed_requests = []
    pagination_links = []
    if form.search_phrase:
        terms = form.search_phrase.split()
        search_interfaces = get_hosting_service_interfaces()
        aggregated_result = fetch_concurrently(terms, search_interfaces)
        results = filter_results(aggregated_result.search_results, form)
        failed_requests = aggregated_result.failed_requests
        results_paginated = results[results_offset:(results_offset + results_per_page)]
        pagination_links = get_page_links(request.full_path, results_offset, results_per_page, len(results))
        search_feedback = get_search_feedback(len(results))

    template_path = "search/search_list.html" if form.search_phrase else "search/landing_page.html"
    return render_template(template_path,
                           form=form,
                           search_results=results_paginated,
                           search_feedback=search_feedback,
                           pagination_links=pagination_links,  # [PageLink] namedtuples
                           failed_requests=failed_requests)  # TODO these errors should be formatted to text that is useful for a enduser


def get_search_feedback(results_total: int) -> str:
    if results_total > 0:
        return "Found {} matching repositories.".format(results_total)
    else:
        return "No matching repositories found."
