from flask import Blueprint, render_template
from flask import current_app as app
from flask import request

from flask_security import login_required
from hubgrep.constants import SITE_TITLE, PARAM_OFFSET, PARAM_PER_PAGE
from hubgrep.lib.pagination import get_page_links
from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces
from hubgrep.models import HostingService

from hubgrep.frontend_blueprint import frontend


def get_search_feedback(results_total: int) -> str:
    if results_total > 0:
        return "Found {} matching repositories.".format(results_total)
    else:
        return "No matching repositories found."


@frontend.route("/")
def index():
    results_paginated = []
    results_offset = int(request.args.get(PARAM_OFFSET, 0))
    results_per_page = int(request.args.get(PARAM_PER_PAGE, app.config['PAGINATION_PER_PAGE_DEFAULT']))
    search_phrase = request.args.get("s", False)
    search_feedback = ""
    external_errors = []
    pagination_links = []
    if search_phrase is not False:
        terms = search_phrase.split()
        search_interfaces = get_hosting_service_interfaces(cache=app.config['ENABLE_CACHE'])
        results, external_errors = fetch_concurrently(terms, search_interfaces)
        results_paginated = results[results_offset:(results_offset + results_per_page)]
        pagination_links = get_page_links(request.full_path, results_offset, results_per_page, len(results))
        search_feedback = get_search_feedback(len(results))

    return render_template("search/search.html",
                           title=SITE_TITLE,
                           search_results=results_paginated,
                           search_url=request.url,
                           search_phrase=search_phrase,
                           search_feedback=search_feedback,
                           pagination_links=pagination_links,  # [PageLink] namedtuples
                           external_errors=external_errors)  # TODO these errors should be formatted to text that is useful for a enduser
