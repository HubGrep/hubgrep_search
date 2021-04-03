from collections import namedtuple
from datetime import datetime
import pytz
from flask import render_template
from flask import current_app as app
from flask import request

from hubgrep.constants import SITE_TITLE, PARAM_OFFSET, PARAM_PER_PAGE, DATE_FORMAT
from hubgrep.lib.pagination import get_page_links
from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.filter_results import filter_results
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces
from hubgrep.frontend_blueprint import frontend

Checkbox = namedtuple("checkbox", "service_id id label is_checked")
utc = pytz.UTC

class SearchForm:
    search_phrase: str
    exclude_service_checkboxes: [Checkbox]
    exclude_forks: bool
    exclude_archived: bool
    created_after: str
    created_before: str
    updated_after: str
    created_after_dt: datetime
    created_before_dt: datetime
    updated_after_dt: datetime

    def __init__(self, search_phrase: str,
                 exclude_service_checkboxes: [Checkbox],
                 exclude_forks: bool,
                 exclude_archived: bool,
                 created_after: str = "",
                 created_before: str = "",
                 updated_after: str = "",
                 created_after_dt: datetime = False,
                 created_before_dt: datetime = False,
                 updated_after_dt: datetime = False):
        self.search_phrase = search_phrase
        self.exclude_service_checkboxes = exclude_service_checkboxes
        self.exclude_forks = exclude_forks
        self.exclude_archived = exclude_archived
        self.created_after = created_after
        self.created_before = created_before
        self.updated_after = updated_after
        self.created_after_dt = created_after_dt
        self.created_before_dt = created_before_dt
        self.updated_after_dt = updated_after_dt


def _get_exclude_service_checkboxes() -> {}:
    exclude_service_checkboxes = dict()
    for service in app.config["CACHED_HOSTING_SERVICES"]:
        is_checked = request.args.get("xs{}".format(service.id), False) == "on"
        exclude_service_checkboxes[service.id] = Checkbox(service_id=service.id, id="xs{}".format(service.id),
                                                  label=service.label, is_checked=is_checked)
    return exclude_service_checkboxes


def _get_search_form() -> SearchForm:
    # we default to "on" for missing checkbox params only when search_phrase is empty (as its the landing page)
    search_phrase = request.args.get("s", "")
    exclude_forks = request.args.get("f", False) == "on"
    exclude_archived = request.args.get("a", False) == "on"
    exclude_service_checkboxes = _get_exclude_service_checkboxes()
    created_after = request.args.get("ca", "")
    created_before = request.args.get("cb", "")
    updated_after = request.args.get("u", "")
    created_after_dt = False
    created_before_dt = False
    updated_after_dt = False
    if created_after != "":
        created_after_dt = utc.localize(datetime.strptime(created_after, DATE_FORMAT))
    if created_before != "":
        created_before_dt = utc.localize(datetime.strptime(created_before, DATE_FORMAT))
    if updated_after != "":
        updated_after_dt = utc.localize(datetime.strptime(updated_after, DATE_FORMAT))

    return SearchForm(search_phrase=search_phrase, exclude_service_checkboxes=exclude_service_checkboxes,
                      exclude_forks=exclude_forks, exclude_archived=exclude_archived,
                      created_after=created_after, created_after_dt=created_after_dt,
                      created_before=created_before, created_before_dt=created_before_dt,
                      updated_after=updated_after, updated_after_dt=updated_after_dt)


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
    form = _get_search_form()
    search_feedback = ""
    external_errors = []
    pagination_links = []
    if form.search_phrase != "":
        terms = form.search_phrase.split()
        search_interfaces = get_hosting_service_interfaces(cache=app.config['ENABLE_CACHE'])
        results, external_errors = fetch_concurrently(terms, search_interfaces)
        results = filter_results(results, form)
        results_paginated = results[results_offset:(results_offset + results_per_page)]
        pagination_links = get_page_links(request.full_path, results_offset, results_per_page, len(results))
        search_feedback = get_search_feedback(len(results))

    return render_template("search/search.html",
                           title=SITE_TITLE,
                           form=form,
                           search_url=request.url,
                           search_results=results_paginated,
                           search_feedback=search_feedback,
                           pagination_links=pagination_links,  # [PageLink] namedtuples
                           external_errors=external_errors)  # TODO these errors should be formatted to text that is useful for a enduser
