from collections import namedtuple
from datetime import datetime
import urllib
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
from hubgrep.frontend_blueprint.routes import get_from_request

Checkbox = namedtuple("checkbox", "service_id id label is_checked")
utc = pytz.UTC


class SearchForm:
    search_phrase: str
    service_checkboxes: [Checkbox]
    include_forks: bool
    include_archived: bool
    created_after: str
    created_before: str
    updated_after: str
    created_after_dt: datetime
    created_before_dt: datetime
    updated_after_dt: datetime

    def __init__(self, search_phrase: str,
                 service_checkboxes: [Checkbox],
                 include_forks: bool,
                 include_archived: bool,
                 created_after: str = "",
                 created_before: str = "",
                 updated_after: str = "",
                 created_after_dt: datetime = False,
                 created_before_dt: datetime = False,
                 updated_after_dt: datetime = False):
        self.search_phrase = search_phrase
        self.service_checkboxes = service_checkboxes
        self.include_forks = include_forks
        self.include_archived = include_archived
        self.created_after = created_after
        self.created_before = created_before
        self.updated_after = updated_after
        self.created_after_dt = created_after_dt
        self.created_before_dt = created_before_dt
        self.updated_after_dt = updated_after_dt

    def get_url_params(self):
        params = dict(
            s=self.search_phrase,
            ca=self.created_after,
            cb=self.created_before,
            u=self.updated_after,
        )
        if self.include_forks:
            params["f"] = "on"
        if self.include_archived:
            params["a"] = "on"
        for service_id, checkbox in self.service_checkboxes.items():
            params[f"s{service_id}"] = "on"

        return params

    @staticmethod
    def get_search_form() -> "SearchForm":
        # we default to "on" for missing checkbox params only when search_phrase is empty (as its the landing page)
        search_phrase = get_from_request("s", "")
        include_forks = search_phrase == "" or get_from_request("f", False) == "on"
        include_archived = search_phrase == "" or get_from_request("a", False) == "on"
        service_checkboxes = SearchForm.get_service_checkboxes(
            is_initial=search_phrase == ""
        )
        created_after = get_from_request("ca", "")
        created_before = get_from_request("cb", "")
        updated_after = get_from_request("u", "")
        created_after_dt = False
        created_before_dt = False
        updated_after_dt = False
        if created_after != "":
            created_after_dt = utc.localize(
                datetime.strptime(created_after, DATE_FORMAT)
            )
        if created_before != "":
            created_before_dt = utc.localize(
                datetime.strptime(created_before, DATE_FORMAT)
            )
        if updated_after != "":
            updated_after_dt = utc.localize(
                datetime.strptime(updated_after, DATE_FORMAT)
            )

        return SearchForm(
            search_phrase=search_phrase,
            service_checkboxes=service_checkboxes,
            include_forks=include_forks,
            include_archived=include_archived,
            created_after=created_after,
            created_after_dt=created_after_dt,
            created_before=created_before,
            created_before_dt=created_before_dt,
            updated_after=updated_after,
            updated_after_dt=updated_after_dt,
        )

    @staticmethod
    def get_service_checkboxes(is_initial=True) -> {}:
        service_checkboxes = dict()
        for service in app.config["CACHED_HOSTING_SERVICES"]:
            is_checked = (
                is_initial or get_from_request("s{}".format(service.id), False) == "on"
            )
            service_checkboxes[service.id] = Checkbox(
                service_id=service.id,
                id="s{}".format(service.id),
                label=service.label,
                is_checked=is_checked,
            )
        return service_checkboxes


@frontend.route("/", methods=["GET", "POST"])
def index():
    results_paginated = []
    results_offset = int(get_from_request(PARAM_OFFSET, 0))
    results_per_page = int(
        get_from_request(PARAM_PER_PAGE, app.config["PAGINATION_PER_PAGE_DEFAULT"])
    )
    form = SearchForm.get_search_form()
    search_feedback = ""
    external_errors = []
    pagination_links = []
    if form.search_phrase != "":
        terms = form.search_phrase.split()
        search_interfaces = get_hosting_service_interfaces(
            cache=app.config["ENABLE_CACHE"]
        )
        results, external_errors = fetch_concurrently(terms, search_interfaces)
        results = filter_results(results, form)
        results_paginated = results[
            results_offset : (results_offset + results_per_page)
        ]
        pagination_links = get_page_links(
            request.full_path, form.get_url_params(), results_offset, results_per_page, len(results)
        )
        search_feedback = "page {} of {} total matching repositories.".format(
            results_offset // results_per_page + 1, len(results)
        )

    return render_template(
        "search/search.html",
        title=SITE_TITLE,
        form=form,
        search_url=request.url,
        search_results=results_paginated,
        search_feedback=search_feedback,
        pagination_links=pagination_links,  # [PageLink] namedtuples
        external_errors=external_errors,
    )  # TODO these errors should be formatted to text that is useful for a enduser
