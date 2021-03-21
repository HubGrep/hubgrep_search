from flask import Blueprint, render_template


frontend = Blueprint("frontend", __name__, template_folder="templates")


from hubgrep.frontend_blueprint.routes.index import index
from hubgrep.frontend_blueprint.routes.about import about
from hubgrep.frontend_blueprint.routes.imprint import imprint
from hubgrep.frontend_blueprint.routes.manage import manage_instance, manage_instances




