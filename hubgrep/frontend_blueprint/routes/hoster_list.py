""" Hosters list page route. """

from flask import render_template, current_app as app
from hubgrep.frontend_blueprint import frontend


@frontend.route("/hosters")
def hosters():
    return render_template(
        "hosters/hoster_list.html",
        hosting_instances=app.config["CACHED_HOSTING_SERVICES"],
    )
