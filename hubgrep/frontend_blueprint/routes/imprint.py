from flask import render_template
from hubgrep.constants import SITE_TITLE, PARAM_OFFSET, PARAM_PER_PAGE

from hubgrep.frontend_blueprint import frontend

@frontend.route("/imprint")
def imprint():
    return render_template("imprint/imprint.html", title=SITE_TITLE)

