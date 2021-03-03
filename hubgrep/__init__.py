import logging
import os
from flask import Flask
from flask_assets import Environment, Bundle
#from flask_migrate import Migrate
#from flask_sqlalchemy import SQLAlchemy

from hubgrep.lib.init_logging import init_logging

#from flask_security import (
    #Security,
    #SQLAlchemyUserDatastore,
    #auth_required,
    #hash_password,
#)

#db = SQLAlchemy()

#migrate = Migrate()
logger = logging.getLogger(__name__)


# fix keep-alive in dev server (dropped connections from client sessions)
from werkzeug.serving import WSGIRequestHandler

WSGIRequestHandler.protocol_version = "HTTP/1.1"


def create_app():
    app = Flask(__name__,
                static_url_path="/static",
                static_folder="static")
    assets = Environment(app)
    scss_search = Bundle('scss/search.scss', filters='pyscss', output='scss_search')
    scss_about = Bundle('scss/about.scss', filters='pyscss', output='scss_about')
    assets.register('scss_about', scss_about)

    @app.after_request
    def add_gnu_tp_header(response):
        # www.gnuterrypratchett.com
        response.headers.add("X-Clacks-Overhead", "GNU Terry Pratchett")
        return response

    app_env = os.environ.get("APP_ENV", "development")
    config_mapping = {
        "development": "hubgrep.config.DevelopmentConfig",
        "production": "hubgrep.config.ProductionConfig",
        "testing": "hubgrep.config.testingConfig",
    }

    app.config.from_object(config_mapping[app_env])

    init_logging(loglevel=app.config["LOGLEVEL"])

    #db.init_app(app)
    #migrate.init_app(app, db=db)

    #user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    #security = Security(app, user_datastore)

    from hubgrep.frontend_blueprint import frontend
    from hubgrep.cli_blueprint import cli_bp

    app.register_blueprint(frontend)
    app.register_blueprint(cli_bp)

    return app
