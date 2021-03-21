from flask import Blueprint, render_template
from flask import current_app as app
from flask import request
from hubgrep.constants import title

from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces
from hubgrep.models import HostingService

frontend = Blueprint("frontend", __name__, template_folder="templates")


@frontend.route("/")
def index():
    repos_per_page = "..."  # TODO hook up the setting for display
    search_phrase = request.args.get("s", False)
    search_results = []
    search_feedback = ""
    external_errors = []
    if search_phrase is not False:
        terms = search_phrase.split()
        search_interfaces = get_hosting_service_interfaces(cache=app.config['ENABLE_CACHE'])
        search_results, external_errors = fetch_concurrently(terms, search_interfaces)
        search_feedback = "{} out of {} total matching repositories.".format(repos_per_page, len(search_results))

    return render_template("search/search.html",
                           title=title,
                           search_results=search_results,
                           search_url=request.url,
                           search_phrase=search_phrase,
                           search_feedback=search_feedback,
                           external_errors=external_errors) # TODO these errors should be formatted to text that is useful for a enduser


@frontend.route("/about")
def about():
    hosting_instances= HostingService.query.all()
    return render_template("about/about.html", title=title, hosting_instances=hosting_instances)

@frontend.route("/imprint")
def imprint():
    return render_template("imprint/imprint.html", title=title)
