import click
from flask import current_app as app
from hubgrep import set_app_cache
from hubgrep.lib.filter_results import filter_results
from hubgrep.lib.fetch_results import fetch_concurrently
from hubgrep.lib.get_hosting_service_interfaces import get_hosting_service_interfaces
from hubgrep.frontend_blueprint.routes.index import SearchForm, get_service_checkboxes

from hubgrep.cli_blueprint import cli_bp


@cli_bp.cli.command()
@click.argument("terms", nargs=-1)
@click.option("--no-forks", is_flag=True, default=False)
@click.option("--no-archived", is_flag=True, default=False)
def search(terms, no_forks, no_archived):
    set_app_cache()
    search_interfaces = get_hosting_service_interfaces(cache=app.config['ENABLE_CACHE'])

    results, errors = fetch_concurrently(terms, search_interfaces)
    for error in errors:
        print(error)

    form = SearchForm(search_phrase=" ".join(terms),
                      exclude_service_checkboxes=get_service_checkboxes(),
                      exclude_forks=no_forks,
                      exclude_archived=no_archived)
    results = filter_results(results, form)
    results.reverse()
    for result in results:
        text = result.get_cli_formatted()
        print(text)
    print(f'({len(results)} results)')
    pass
