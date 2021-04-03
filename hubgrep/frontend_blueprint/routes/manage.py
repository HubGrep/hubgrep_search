from flask import render_template
from flask import request
from flask import abort
from flask import flash
from flask import redirect
from flask import url_for
from flask_security import current_user

from flask_security import login_required
from hubgrep.models import HostingService

from hubgrep import db, security
from hubgrep.frontend_blueprint import frontend
from hubgrep.frontend_blueprint.forms.edit_hosting_service import HostingServiceForm, HostingServiceFirstStep
from hubgrep.lib.get_hosting_service_interfaces import hosting_service_interfaces_by_name


@frontend.route("/manage")
@login_required
def manage_instances():
    hosting_service_instances_by_user = {}
    if current_user.has_role("admin"):
        for instance in HostingService.query.all():
            email = instance.user.email
            if not hosting_service_instances_by_user.get(email):
                hosting_service_instances_by_user[email] = []
            hosting_service_instances_by_user[email].append(instance)
        is_admin = True
    else:
        hosting_service_instances_by_user[current_user.email] = current_user.hosting_services
        is_admin = False

    return render_template(
                "management/hosting_service_list.html",
                hosting_services=hosting_service_instances_by_user,
                is_admin=is_admin
            )


@frontend.route("/manage/<hosting_service_id>", methods=['GET', 'POST', ],)
@login_required
def manage_instance(hosting_service_id):
    h: HostingService = HostingService.query.get(hosting_service_id)
    if h.user == current_user or current_user.has_role('admin'):
        pass
    else:
        abort(404)

    form = HostingServiceForm()
    if form.validate_on_submit():
        h.api_url = form.api_url.data
        h.landingpage_url = form.landingpage_url.data
        h.type = form.type.data
        h.config = form.config.data
        db.session.add(h)
        db.session.commit()

    form.type.data = h.type
    form.landingpage_url.data = h.landingpage_url
    form.api_url.data = h.api_url
    form.config.data = h.config
    if form.errors:
        flash(form.errors, "error")
  
    return render_template("management/edit_hosting_service.html", form=form)

