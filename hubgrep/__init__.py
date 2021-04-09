import logging
import os
from flask import Flask, request
from flask_babel import Babel
from flask_assets import Environment, Bundle
from flask_redis import FlaskRedis

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
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

redis_client = FlaskRedis()
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

    _build_assets(assets)

    @app.after_request
    def add_gnu_tp_header(response):
        # www.gnuterrypratchett.com
        response.headers.add("X-Clacks-Overhead", "GNU Terry Pratchett")
        return response

    app_env = os.environ.get("APP_ENV", "development")
    config_mapping = {
        "build": "hubgrep.config.BuildConfig",
        "development": "hubgrep.config.DevelopmentConfig",
        "production": "hubgrep.config.ProductionConfig",
        "testing": "hubgrep.config.testingConfig",
    }

    app.config.from_object(config_mapping[app_env])
    babel = Babel(app)
    redis_client.init_app(app)

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

    @app.before_first_request
    def post_setup():
        set_app_cache()

    return app


def set_app_cache():
    # used to avoid calling the db on every request for common almost-static models
    from flask import current_app as app
    from hubgrep.models import HostingService
    app.config["CACHED_HOSTING_SERVICES"] = HostingService.query.all()


def _build_assets(assets: Environment):
    # TODO we dont want to do this with watchers for prod, only for localdev
    scss_about = Bundle(
        "scss/about.scss",
        filters="pyscss",
        depends=["**/*.scss", "**/**/*.scss"],
        output="css/about.css",
    )
    scss_search = Bundle(
        "scss/search.scss",
        filters="pyscss",
        depends=["**/*.scss", "**/**/*.scss"],
        output="css/search.css",
    )
    scss_search_empty = Bundle(
        "scss/search_empty.scss",
        filters="pyscss",
        depends=["**/*.scss", "**/**/*.scss"],
        output="css/search_empty.css",
    )
    hosting_service_management = Bundle(
        "scss/hosting_service_management.scss",
        filters="pyscss",
        depends=["**/*.scss", "**/**/*.scss"],
        output="css/hosting_service_management.css",
    )
    assets.register("scss_about", scss_about)
    assets.register("scss_search", scss_search)
    assets.register("scss_search_empty", scss_search_empty)
    assets.register("scss_hosting_service_management", hosting_service_management)
