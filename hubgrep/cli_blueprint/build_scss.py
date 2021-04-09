import os
import click
import json
from hubgrep.cli_blueprint import cli_bp

from hubgrep import redis_client

from sassutils.builder import Manifest

from flask import current_app as app
from tempfile import TemporaryDirectory

def delete_empty_folders(base_path):
    # https://stackoverflow.com/a/64025990
    walk = list(os.walk(base_path))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            os.rmdir(path)

@cli_bp.cli.command()
def build_scss():
    manifests = Manifest.normalize_manifests(app.config["SASS_MANIFEST"])

    for package_name, manifest in manifests.items():
        css_files = manifest.build("hubgrep/", output_style=app.config.get("CSS_OUTPUT_STYLE", "compressed"))

    print(f"built css files: {list(css_files)}") 
    print("deleting empty folders...")
    delete_empty_folders("hubgrep/static/")
