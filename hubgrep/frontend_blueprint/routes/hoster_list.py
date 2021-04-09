from flask import render_template
from flask import render_template, current_app as app
from hubgrep.constants import SITE_TITLE, PARAM_OFFSET, PARAM_PER_PAGE

from hubgrep.frontend_blueprint import frontend


@frontend.route("/hosters")
def hosters():
    return render_template(
        "hosters/hoster_list.html",
        title=SITE_TITLE,
        hosting_instances=app.config["CACHED_HOSTING_SERVICES"],
    )
