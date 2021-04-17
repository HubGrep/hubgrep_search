import logging
import os
from flask import Flask, request
from flask_babel import Babel
from flask_assets import Environment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from sassutils.wsgi import SassMiddleware

from hubgrep.constants import APP_ENV_BUILD, APP_ENV_TESTING, APP_ENV_DEVELOPMENT, APP_ENV_PRODUCTION, SITE_TITLE
from hubgrep.lib.init_logging import init_logging

from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    auth_required,
    hash_password,
)

db = SQLAlchemy()
security = Security()
migrate = Migrate()
mail = Mail()

logger = logging.getLogger(__name__)

# fix keep-alive in dev server (dropped connections from client sessions)
from werkzeug.serving import WSGIRequestHandler

WSGIRequestHandler.protocol_version = "HTTP/1.1"


def create_app():
    app = Flask(__name__, static_url_path="/static", static_folder="static")
    assets = Environment(app)

    # disable cache, because that breaks
    # prod build for some reason.
    # maybe add to the flask config?
    assets.cache = False
    assets.manifest = False

    @app.after_request
    def add_gnu_tp_header(response):
        # www.gnuterrypratchett.com
        response.headers.add("X-Clacks-Overhead", "GNU Terry Pratchett")
        return response

    config_mapping = {
        APP_ENV_BUILD: "hubgrep.config.BuildConfig",
        APP_ENV_DEVELOPMENT: "hubgrep.config.DevelopmentConfig",
        APP_ENV_PRODUCTION: "hubgrep.config.ProductionConfig",
        APP_ENV_TESTING: "hubgrep.config.TestingConfig",
    }
    app_env = os.environ.get("APP_ENV", APP_ENV_DEVELOPMENT)
    app.config.from_object(config_mapping[app_env])

    if app.config['WATCH_SCSS']:
        app.wsgi_app = SassMiddleware(app.wsgi_app, app.config["SASS_MANIFEST"])

    babel = Babel(app)

    init_logging(loglevel=app.config["LOGLEVEL"])

    db.init_app(app)
    migrate.init_app(app, db=db)
    mail.init_app(app)

    # import after db is created
    from hubgrep.models import User, Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
    from hubgrep.frontend_blueprint import frontend
    from hubgrep.cli_blueprint import cli_bp

    app.register_blueprint(frontend)
    app.register_blueprint(cli_bp)

    @babel.localeselector
    def get_locale():
        lang = request.accept_languages.best_match(app.config["LANGUAGES"].keys())
        return lang

    app.jinja_env.globals["get_locale"] = get_locale
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    @app.before_first_request
    def post_setup():
        set_app_cache()

    @app.context_processor
    def inject_title():
        return dict(title=SITE_TITLE)  # always expose these in templates

    return app


def set_app_cache():
    # used to avoid calling the db on every request for common almost-static models
    from flask import current_app as app
    from hubgrep.models import HostingService
    app.config["CACHED_HOSTING_SERVICES"] = HostingService.query.all()
