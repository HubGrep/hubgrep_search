import click
import json
from hubgrep.cli_blueprint import cli_bp

from hubgrep import redis_client


@cli_bp.cli.command()
@click.argument("path", type=click.Path(exists=True))
def add_hosters(path):
    with open(path, 'r') as f:
        hosters = json.load(f)

    for name, config in hosters.items():
        redis_client.set(f'hosting_service:{name}', json.dumps(config))


@cli_bp.cli.command()
def list_hosters():
    for key in redis_client.keys('hosting_service:*'):
        print(redis_client.get(key))
@cli_bp.cli.command()
def flush_hosters():
    for key in redis_client.keys('hosting_service:*'):
        print(redis_client.delete(key))

