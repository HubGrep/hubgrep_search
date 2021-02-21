import click
from flask import Blueprint, render_template
from flask import current_app as app, request
from hubgrep_meta.lib.fetch_results import fetch_concurrently

cli_bp = Blueprint("cli", __name__)


@cli_bp.cli.command()
@click.argument('terms', nargs=-1)
def search(terms):

    search_interfaces = app.config["SEARCH_INTERFACES_BY_NAME"].values()
    results, errors = fetch_concurrently(terms, search_interfaces)
    for error in errors:
        print(error)
    for result in results:

        text = result.get_cli_formatted()
        print(text)
    pass

