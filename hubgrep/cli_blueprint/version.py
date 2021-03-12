from hubgrep.cli_blueprint import cli_bp

@cli_bp.cli.command()
def version():
    print(f'HubGrep {cli_bp.config.VERSION}')
