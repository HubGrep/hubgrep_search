""" Add instance page routes. """

import logging
from urllib.parse import urljoin

from flask import render_template
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import current_app

import requests

from hubgrep.frontend_blueprint import frontend
from hubgrep.frontend_blueprint.forms.hosting_service.hosting_services import (
    HostingServiceForm,
    NoHostingServiceFormException,
)
from hubgrep.frontend_blueprint.forms.hosting_service.hosting_service_first_step import (
    HostingServiceFormFirstStep,
)

logger = logging.getLogger(__name__)


@frontend.route("/add_instance/step_1", methods=["GET", "POST"])
def add_instance_step_1():
    form = HostingServiceFormFirstStep()
    if form.validate_on_submit():
        landingpage_url = form.landingpage_url.data
        _type = form.type.data

        step_2 = url_for(
            "frontend.add_instance_step_2",
            type=_type,
            landingpage_url=landingpage_url,
        )

        return redirect(step_2)

    form.landingpage_url.data = request.form.get("landingpage_url", "")
    form.type.data = request.form.get("type", "")

    if form.errors:
        flash(form.errors, "error")

    return render_template("management/add_hosting_service_1.html", form=form)


@frontend.route("/add_instance/step_2/", methods=["GET", "POST"])
def add_instance_step_2():
    """
    second step in hoster adding
    works without the first step in theory, since that only helps filling in the api url.
    """
    hoster_type = request.args.get("type", "")
    try:
        form = HostingServiceForm.from_hosting_service_type(hoster_type)
    except NoHostingServiceFormException:
        flash("unknown hoster type!")
        return redirect(url_for("frontend.hosters"))

    # if the form doesnt have data, take it from the url
    if not form.landingpage_url.data:
        form.landingpage_url.data = request.args.get("landingpage_url", "")
    if not form.type.data:
        form.type.data = request.args.get("type", "")
    if not form.api_url.data:
        form.populate_api_url()

    if form.validate_on_submit():
        hosting_service = form.to_hosting_service()
        hosting_service_dict = hosting_service.to_dict()
        indexer_hoster_url = urljoin(current_app.config["INDEXER_URL"], "api/v1/hosters")
        response = None
        try:
            # try to add this hoster to the indexer
            response = requests.post(indexer_hoster_url, json=hosting_service_dict)
        except Exception:
            logger.exception("could not contact indexer!")
            flash("Something seems to be wrong with the indexing service. Try again later or shoot us a mail!")

        if response and response.ok:
            if response.json().get("added", False):
                flash("New hoster added! It should be included in the search results in a few hours!", "success")
                return redirect(url_for("frontend.search"))
            elif response.json().get("reason", False):
                # todo: map the reasons from indexer /hosters to some messages in babel
                flash(f"could not add hoster to the indexing service: {response.json()['reason']}")
            else:
                # todo: embed a mail address here?
                flash("Something seems to be wrong with the indexing service. Try again later or shoot us a mail!")
        else:
            flash("Something seems to be wrong with the indexing service. Try again later or shoot us a mail!")

    if form.errors:
        flash(form.errors, "error")

    return render_template("management/add_hosting_service_2.html", form=form)
