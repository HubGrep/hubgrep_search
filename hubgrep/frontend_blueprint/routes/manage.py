from flask import render_template
from flask import request
from flask_security import current_user

from flask_security import login_required
from hubgrep.models import HostingService

from hubgrep.frontend_blueprint import frontend



@frontend.route('/manage')
@login_required
def manage_instances():
    # todo: show instance health
    if current_user.has_role('admin'):
        hosting_service_instances = HostingService.query.all()
    else:
        hosting_service_instances = current_user.hosting_services
    
    return render_template("management/hosting_service_list.html", hosting_services=hosting_service_instances)


@frontend.route('/manage/<hosting_service_id>')
@login_required
def manage_instance(hosting_service_id):
    return render_template("management/hosting_service.html")
