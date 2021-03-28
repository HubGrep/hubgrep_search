from flask import render_template, current_app as app
from hubgrep.constants import SITE_TITLE
from hubgrep.frontend_blueprint import frontend


@frontend.route("/about")
def about():
    return render_template("about/about.html",
                           title=SITE_TITLE,
                           hosting_instances=app.config["CACHED_HOSTING_SERVICES"])
