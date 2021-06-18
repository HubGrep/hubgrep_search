""" Manage page route. """

from flask import render_template
from flask import abort
from flask import flash
from flask import redirect
from flask import url_for
from flask_security import current_user

from flask_security import login_required
from hubgrep.models import HostingService

from hubgrep import db, set_app_cache
from hubgrep.frontend_blueprint import frontend
from hubgrep.frontend_blueprint.forms.hosting_service.hosting_services import (
    HostingServiceForm,
    NoHostingServiceFormException,
)
from hubgrep.frontend_blueprint.forms.hosting_service.hosting_service_first_step import (
    HostingServiceFormFirstStep,
)
from hubgrep.frontend_blueprint.forms.confirm import ConfirmForm


@frontend.route("/manage")
@login_required
def manage_instances():
    hosting_service_instances_by_user = {}
    if current_user.has_role("admin"):
        for instance in HostingService.query.all():
            if instance.user:
                email = instance.user.email
            else:
                email = "anonymous user"
            if not hosting_service_instances_by_user.get(email):
                hosting_service_instances_by_user[email] = []
            hosting_service_instances_by_user[email].append(instance)
    else:
        hosting_service_instances_by_user[
            current_user.email
        ] = current_user.hosting_services

    return render_template(
        "management/hosting_service_list.html",
        hosting_services=hosting_service_instances_by_user,
    )


@frontend.route("/manage/<hosting_service_id>", methods=["GET", "POST"])
@login_required
def manage_instance(hosting_service_id):
    h: HostingService = HostingService.query.get(hosting_service_id)
    if h.user == current_user or current_user.has_role("admin"):
        pass
    else:
        abort(404)

    try:
        form = HostingServiceForm.from_hosting_service(h)
    except NoHostingServiceFormException:
        flash("unknown hoster type!")
        return redirect("frontend.manage_instances")

    if form.validate_on_submit():
        h.api_url = form.api_url.data
        h.landingpage_url = form.landingpage_url.data
        h.type = form.type.data
        h.api_key = form.api_key.data
        h.custom_config = form.custom_config.data
        db.session.add(h)
        db.session.commit()
        set_app_cache()

    if form.errors:
        flash(form.errors, "error")

    if h.user:
        owner = h.user.email
    else:
        owner = "anonymous user"

    return render_template(
        "management/edit_hosting_service.html", form=form, owner=owner
    )


@frontend.route("/manage/<hosting_service_id>/delete", methods=["GET", "POST"])
@login_required
def delete_instance(hosting_service_id):
    h: HostingService = HostingService.query.get(hosting_service_id)
    if h.user == current_user or current_user.has_role("admin"):
        pass
    else:
        abort(404)

    form = ConfirmForm()
    if form.validate_on_submit():
        db.session.delete(h)
        db.session.commit()
        set_app_cache()
        flash("hoster deleted", "success")
        return redirect(url_for("frontend.manage_instances"))

    if form.errors:
        flash(form.errors, "error")

    confirm_question = (
        f'Do you really want to delete "{h.label}" for user "{h.user.email}"?'
    )
    confirm_button_text = f"confirm"

    return render_template(
        "management/confirm.html",
        form=form,
        owner=h.user.email,
        confirm_question=confirm_question,
        confirm_button_text=confirm_button_text,
    )
