from flask import render_template
from flask import request
from flask import abort
from flask import flash
from flask import redirect
from flask import url_for

from flask_security import current_user
from flask_security import login_required

from hubgrep import db
from hubgrep.frontend_blueprint import frontend
from hubgrep.frontend_blueprint.forms.edit_hosting_service import (
    HostingServiceForm,
    HostingServiceFirstStep,
)
from hubgrep.lib.get_hosting_service_interfaces import (
    hosting_service_interfaces_by_name,
)
from hubgrep.models import HostingService, get_service_label_from_url


@frontend.route("/add_instance/step_1", methods=["GET", "POST"])
@login_required
def add_instance_step_1():
    form = HostingServiceFirstStep()
    if form.validate_on_submit():
        print("valid")
        landingpage_url = form.landingpage_url.data
        _type = form.type.data

        s2 = url_for(
            "frontend.add_instance_step_2",
            type=_type,
            landingpage_url=landingpage_url,
        )

        return redirect(s2)
    else:
        print("didnt validate")
    form.landingpage_url.data = request.form.get("landingpage_url", "")
    form.type.data = request.form.get("type", "")

    if form.errors:
        flash(form.errors, "error")

    return render_template("management/add_hosting_service_1.html", form=form)


@frontend.route("/add_instance/step_2/", methods=["GET", "POST"])
@login_required
def add_instance_step_2():
    form = HostingServiceForm()
    form.landingpage_url.data = request.args.get("landingpage_url", "")
    form.type.data = request.args.get("type", "")

    form.populate_api_url()

    if form.validate_on_submit():
        HostingServiceInterface = hosting_service_interfaces_by_name.get(
            form.type.data, False
        )
        if not HostingServiceInterface:
            flash(f'hosting interface for "{form.type.data}" not found!', "error")
            return render_template("management/add_hosting_service_2.html", form=form)

        if HostingService.query.filter_by(api_url=form.api_url.data).first():
            flash(f'hoster "{form.api_url.data}" already exists!', "error")
            return render_template("management/add_hosting_service_2.html", form=form)

        h = HostingService()

        h.user_id = current_user.id

        h.api_url = form.api_url.data
        h.landingpage_url = form.landingpage_url.data
        h.type = form.type.data
        h.config = form.config.data
        h.label = get_service_label_from_url(form.landingpage_url.data)

        db.session.add(h)
        db.session.commit()

        flash("new hoster added!", "success")

        return redirect(url_for("frontend.manage_instances"))

    return render_template("management/add_hosting_service_2.html", form=form)
