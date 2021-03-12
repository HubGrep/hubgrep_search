from flask import Blueprint, render_template
from flask import current_app as app
from flask import request
from hubgrep.constants import title

from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.search_interfaces import get_search_interfaces

frontend = Blueprint("frontend", __name__, template_folder="templates")

@frontend.route("/")
def index():
    search_phrase = request.args.get("s", False)
    search_results = []
    if search_phrase is not False:
        terms = search_phrase.split()
        search_interfaces = get_search_interfaces(cache=app.config['ENABLE_CACHE'])
        search_results, external_errors = fetch_concurrently(terms, search_interfaces)

    return render_template("search/search.html", title=title, search_results=search_results, search_url=request.url, search_phrase=search_phrase)

@frontend.route("/about")
def about():
    return render_template("about/about.html", title=title)
