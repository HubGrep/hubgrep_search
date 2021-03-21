from flask import render_template
from flask import request
from flask import abort
from flask import flash
from flask_security import current_user

from flask_security import login_required
from hubgrep.models import HostingService

from hubgrep import db, security
from hubgrep.frontend_blueprint import frontend
from hubgrep.frontend_blueprint.forms.edit_hosting_service import HostingServiceForm

@frontend.route("/manage")
@login_required
def manage_instances():
    # todo: show instance health
    if current_user.has_role("admin"):
        hosting_service_instances = HostingService.query.all()
        is_admin = True
    else:
        hosting_service_instances = current_user.hosting_services
        is_admin = False

    return render_template(
        "management/hosting_service_list.html",
        hosting_services=hosting_service_instances,
        is_admin=is_admin,
    )


@frontend.route("/manage/<hosting_service_id>", methods=['GET', 'POST', ])
@login_required
def manage_instance(hosting_service_id):
    h: HostingService = HostingService.query.get(hosting_service_id)
    if h.user == current_user or current_user.has_role('admin'):
        pass
    else:
        abort(404)

    form = HostingServiceForm()
    if form.validate_on_submit():
        print("validating")
        h.base_url = form.base_url.data
        h.type = form.base_url.data
        h.frontpage_url = form.frontpage_url.data
        h.type = form.type.data
        h.config = form.config.data
        db.session.add(h)
        db.session.commit()

    form.base_url.data = h.base_url
    form.type.data = h.type
    form.frontpage_url.data = h.frontpage_url
    form.base_url.data = h.base_url
    form.config.data = h.config
    flash(form.errors, "error")
  
    return render_template("management/edit_hosting_service.html", form=form)
