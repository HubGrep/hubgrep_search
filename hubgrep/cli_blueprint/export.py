import os
import click
import json
from hubgrep.cli_blueprint import cli_bp

from hubgrep import db, security
from hubgrep.models import HostingService

@cli_bp.cli.command()
def export_hosters():
    hosters = []
    for h in HostingService.query.all():
        hosters.append(h.to_dict())

    print(json.dumps(hosters, indent=2))


