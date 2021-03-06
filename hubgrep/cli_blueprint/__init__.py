import click
from flask import Blueprint, render_template
from flask import current_app as app, request
from hubgrep.lib.fetch_results import filter_results
from hubgrep.lib.fetch_results import fetch_concurrently

cli_bp = Blueprint("cli", __name__)


@cli_bp.cli.command()
@click.argument("terms", nargs=-1)
@click.option("--no-forks", is_flag=True, default=False)
@click.option("--no-archived", is_flag=True, default=False)
def search(terms, no_forks, no_archived):

    search_interfaces = app.config["SEARCH_INTERFACES_BY_NAME"].values()
    include_fork = not no_forks
    include_archived = not no_archived

    print(f'include archived: {include_archived}')

    results, errors = fetch_concurrently(terms, search_interfaces)
    for error in errors:
        print(error)


    results = filter_results(results, include_archived=include_archived, include_fork=include_fork)

    for result in results:

        text = result.get_cli_formatted()
        print(text)
    print(f'({len(results)} results)')
    pass
