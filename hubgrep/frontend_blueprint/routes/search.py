""" Search page route. """

import time

from flask import render_template
from flask import current_app as app
from flask import request

from hubgrep.constants import PARAM_OFFSET, PARAM_PER_PAGE, FORM_ARGS
from hubgrep.lib.pagination import get_page_links
from hubgrep.lib.manticore import ManticoreSearch, SearchMeta
from hubgrep.lib.manticore import UserError
from hubgrep.lib.search_form import SearchForm
from hubgrep.frontend_blueprint import frontend

import logging

logger = logging.getLogger(__name__)


@frontend.route("/")
def search():
    total_time = time.time()
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
    results_page = []
    user_errors = []
    pagination_links = []
    meta = SearchMeta([])
    if form.search_phrase:
        try:
            results_page, meta = ManticoreSearch.search(
                form.search_phrase,
                results_offset=results_offset,
                results_per_page=results_per_page,
                exclude_hosting_service_ids=form.get_excluded_hosting_service_ids(),
                exclude_forks=form.exclude_forks,
                exclude_archived=form.exclude_archived,
                exclude_mirror=form.exclude_mirror,
                exclude_empty=form.exclude_empty,
                created_after=form.created_after_dt,
                created_before=form.created_before_dt,
                updated_after=form.updated_after_dt,
                pushed_after=form.pushed_after_dt,
            )
        except UserError as e:
            user_errors.append(e)

        if meta.warning:
            user_errors.append(meta.warning)

        pagination_links = get_page_links(request.full_path, results_offset, results_per_page, meta.total)

    template_path = (
        "search/search_list.html" if form.search_phrase else "search/landing_page.html"
    )
    # obviously we are missing the time it takes to render and respond
    # - but we measure our own "total" to give a more realistic time
    total_time = time.time() - total_time
    logger.info(f"search backend-processing took {total_time}s - engine-only took {meta.time}s")
    return render_template(
        template_path,
        form=form,
        search_results=results_page,
        search_meta=meta,
        total_time=total_time,
        pagination_links=pagination_links,
        user_errors=user_errors,
    )
