from flask import render_template
from hubgrep.constants import SITE_TITLE, PARAM_OFFSET, PARAM_PER_PAGE
from hubgrep.models import HostingService

from hubgrep.frontend_blueprint import frontend

@frontend.route("/about")
def about():
    hosting_instances= HostingService.query.all()
    return render_template("about/about.html", title=SITE_TITLE, hosting_instances=hosting_instances)

