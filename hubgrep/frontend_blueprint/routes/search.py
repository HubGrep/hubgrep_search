""" Search page route. """

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
        exclude_disabled=request.args.get(FORM_ARGS.exclude_disabled, "") == "on",
        exclude_mirror=request.args.get(FORM_ARGS.exclude_mirror, "") == "on",
        created_after=request.args.get(FORM_ARGS.created_after, ""),
        created_before=request.args.get(FORM_ARGS.created_before, ""),
        updated_after=request.args.get(FORM_ARGS.updated_after, ""),
    )
    search_feedback = ""
    user_errors = []
    pagination_links = []
    if form.search_phrase:
        try:
            results = SphinxSearch.search(
                form.search_phrase,
                exclude_hosting_service_ids=form.get_excluded_hosting_service_ids(),
                exclude_forks=form.exclude_forks,
                exclude_archived=form.exclude_archived,
                exclude_disabled=form.exclude_disabled,
                exclude_mirror=form.exclude_mirror,
                created_after=form.created_after_dt,
                created_before=form.created_before_dt,
                updated_after=form.updated_after_dt
            )
        except UserError as e:
            results = []
            user_errors.append(e)

        results_paginated = results[results_offset:(results_offset + results_per_page)]
        pagination_links = get_page_links(request.full_path, results_offset, results_per_page, len(results))
        search_feedback = get_search_feedback(len(results))

    template_path = (
        "search/search_list.html" if form.search_phrase else "search/landing_page.html"
    )
    return render_template(
        template_path,
        form=form,
        search_results=results_paginated,
        search_feedback=search_feedback,
        pagination_links=pagination_links,
        user_errors=user_errors,
    )


def get_search_feedback(results_total: int) -> str:
    """Get a readable message for how a search performed."""
    if results_total > 0:
        return "Found {} matching repositories.".format(results_total)
    else:
        return "No matching repositories found."
