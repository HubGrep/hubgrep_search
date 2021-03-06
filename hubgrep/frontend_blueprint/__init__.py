from flask import Blueprint, render_template
from flask import current_app as app
from flask import request
from hubgrep.constants import title

from hubgrep.lib.fetch_results import fetch_concurrently

frontend = Blueprint("frontend", __name__, template_folder="templates")

@frontend.route("/")
def index():
    search_phrase = request.args.get("s", False)
    search_results = []
    if search_phrase is not False:
        terms = search_phrase.split()
        search_interfaces = app.config["SEARCH_INTERFACES_BY_NAME"].values()
        search_results, external_errors = fetch_concurrently(terms, search_interfaces)

    return render_template("search/search.html", title=title, search_results=search_results, search_url=request.url)

@frontend.route("/about")
def about():
    return render_template("about/about.html", title=title)
