""" Add instance page routes. """

from flask import render_template
from flask import request
from flask import abort
from flask import flash
from flask import redirect
from flask import url_for

from flask_security import current_user
from flask_security import login_required

from hubgrep import db, set_app_cache
from hubgrep.frontend_blueprint import frontend
from hubgrep.frontend_blueprint.forms.hosting_service import  HostingServiceFormFirstStep
from hubgrep.lib.hosting_service_interfaces import hosting_service_interface_mapping
from hubgrep.models import HostingService
from hubgrep.frontend_blueprint.forms.hosting_service.hosting_service_base import HostingServiceForm, NoHostingServiceFormException


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
    hoster_type = request.args.get("type", "")
    try:
        form = HostingServiceForm.from_hosting_service_type(hoster_type)
    except NoHostingServiceFormException:
        flash("unknown hoster type!")
        return redirect("frontend.manage_instances")

    form.landingpage_url.data = request.args.get("landingpage_url", "")
    form.type.data = request.args.get("type", "")

    if not form.api_url.data:
        form.populate_api_url()

    if form.validate_on_submit():
        if HostingService.query.filter_by(api_url=form.api_url.data).first():
            flash(f'hoster "{form.api_url.data}" already exists!', "error")
            return render_template("management/add_hosting_service_2.html", form=form)

        h = form.to_hosting_service()
        if current_user:
            h.user_id = current_user.id
        db.session.add(h)
        db.session.commit()
        set_app_cache()

        flash("new hoster added!", "success")

        if current_user:
            return redirect(url_for("frontend.manage_instances"))
        return redirect(url_for("frontend.search"))

    if form.errors:
        flash(form.errors, "error")

    return render_template("management/add_hosting_service_2.html", form=form)
