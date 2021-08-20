""" Search page route. """

import time

from flask import render_template
from flask import current_app as app
from flask import request
from flask import flash

from hubgrep.constants import PARAM_OFFSET, PARAM_PER_PAGE, FORM_ARGS
from hubgrep.lib.pagination import get_page_links
from hubgrep.lib.sphinx import SphinxSearch
from hubgrep.lib.sphinx import UserError
from hubgrep.lib.search_form import SearchForm
from hubgrep.frontend_blueprint import frontend

import logging

logger = logging.getLogger(__name__)


@frontend.route("/")
def search():
    results_paginated = []
    results_offset = int(request.args.get(PARAM_OFFSET, 0))
    results_per_page = int(
        request.args.get(PARAM_PER_PAGE, app.config["PAGINATION_PER_PAGE_DEFAULT"])
    )
    form = SearchForm(
        search_phrase=request.args.get(FORM_ARGS.search_phrase, ""),
        exclude_service_checkboxes=SearchForm.get_request_service_checkboxes(),
        exclude_forks=request.args.get(FORM_ARGS.exclude_forks, "") == "on",
        exclude_archived=request.args.get(FORM_ARGS.exclude_archived, "") == "on",
        exclude_mirror=request.args.get(FORM_ARGS.exclude_mirror, "") == "on",
        exclude_empty=request.args.get(FORM_ARGS.exclude_empty, "") == "on",
        created_after=request.args.get(FORM_ARGS.created_after, ""),
        created_before=request.args.get(FORM_ARGS.created_before, ""),
        updated_after=request.args.get(FORM_ARGS.updated_after, ""),
        pushed_after=request.args.get(FORM_ARGS.pushed_after, ""),
    )
    user_errors = []
    pagination_links = []
    total_found = 0
    time_search = None
    if form.search_phrase:
        time_before = time.time()
        try:
            results, total_found = SphinxSearch.search(
                form.search_phrase,
                exclude_hosting_service_ids=form.get_excluded_hosting_service_ids(),
                exclude_forks=form.exclude_forks,
                exclude_archived=form.exclude_archived,
                exclude_mirror=form.exclude_mirror,
                exclude_empty=form.exclude_empty,
                created_after=form.created_after_dt,
                created_before=form.created_before_dt,
                updated_after=form.updated_after_dt,
                pushed_after=form.pushed_after_dt
            )
        except UserError as e:
            results = []
            user_errors.append(e)
        time_search = time.time() - time_before

        results_paginated = results[results_offset:(results_offset + results_per_page)]
        pagination_links = get_page_links(request.full_path, results_offset, results_per_page, len(results))

    template_path = (
        "search/search_list.html" if form.search_phrase else "search/landing_page.html"
    )
    return render_template(
        template_path,
        form=form,
        search_results=results_paginated,
        search_total=total_found,
        search_time=time_search,
        pagination_links=pagination_links,
        user_errors=user_errors,
    )
