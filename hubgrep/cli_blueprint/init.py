import logging
import os
from hubgrep.cli_blueprint import cli_bp

from hubgrep.lib.create_admin import create_admin

logger = logging.getLogger(__name__)


@cli_bp.cli.command()
def init():
    admin_email = os.environ["HUBGREP_ADMIN_EMAIL"]
    admin_password = os.environ["HUBGREP_ADMIN_PASSWORD"]

    admin = create_admin(admin_email, admin_password)

    print(f'created {admin}')



