import click
from hubgrep.cli_blueprint import cli_bp


import shutil

@cli_bp.cli.command(help="copy static files to another folder")
@click.argument("target_path", type=click.Path(exists=True))
def copy_static(target_path):
    print(f'copying static files to {target_path}')
    shutil.copytree("hubgrep/static", target_path, dirs_exist_ok=True)

