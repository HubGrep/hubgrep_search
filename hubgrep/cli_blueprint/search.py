import click
from flask import current_app as app
from hubgrep.lib.filter_results import filter_results
from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces

from hubgrep.cli_blueprint import cli_bp


@cli_bp.cli.command()
@click.argument("terms", nargs=-1)
@click.option("--no-forks", is_flag=True, default=False)
@click.option("--no-archived", is_flag=True, default=False)
def search(terms, no_forks, no_archived):

    search_interfaces = get_hosting_service_interfaces(cache=app.config['ENABLE_CACHE'])
    include_fork = not no_forks
    include_archived = not no_archived

    print(f'include archived: {include_archived}')

    results, errors = fetch_concurrently(terms, search_interfaces)
    for error in errors:
        print(error)


    results = filter_results(results, include_archived=include_archived, include_fork=include_fork)
    results.reverse()
    for result in results:

        text = result.get_cli_formatted()
        print(text)
    print(f'({len(results)} results)')
    pass
