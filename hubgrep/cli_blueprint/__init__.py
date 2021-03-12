import click
from flask import Blueprint, render_template
from flask import current_app as app, request
from hubgrep.lib.fetch_results import filter_results
from hubgrep.lib.fetch_results import fetch_concurrently

cli_bp = Blueprint("cli", __name__)

from hubgrep.cli_blueprint.version import version
from hubgrep.cli_blueprint.search import search
from hubgrep.cli_blueprint.read_hosters_json import add_hosters, list_hosters


