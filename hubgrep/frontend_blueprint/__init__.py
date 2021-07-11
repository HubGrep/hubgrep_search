from flask import Blueprint

frontend = Blueprint("frontend", __name__, template_folder="templates")

from hubgrep.frontend_blueprint.routes.search import search
from hubgrep.frontend_blueprint.routes.about import about
from hubgrep.frontend_blueprint.routes.hoster_list import hosters
from hubgrep.frontend_blueprint.routes.add_instance import add_instance_step_1, add_instance_step_2
