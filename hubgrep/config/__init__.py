"""
HubGrep environment configurations.
"""
import os
from hubgrep.constants import HOSTING_SERVICE_REQUEST_TIMEOUT_DEFAULT


class Config:
    """Base configuration."""

    # hardcoded config
    DEBUG = False
    TESTING = False
    LOGLEVEL = "debug"
    VERSION = "0.1.0"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"
    LANGUAGES = {"en": "English", "de": "Deutsch"}

    REFERER = f"HubGrep v{VERSION}"

    PAGINATION_PER_PAGE_DEFAULT = 10

    SASS_MANIFEST = {
        "hubgrep": (
            "frontend_blueprint/templates",
            "static/css",
            "/static/css",
            True,
        )  # 4th val = strip_extensions
    }

    WATCH_SCSS = False


class _EnvironmentConfig:
    # user defined config
    MAIL_DEBUG = os.environ.get("HUBGREP_MAIL_DEBUG", False)

    MAIL_SERVER = os.environ.get("HUBGREP_MAIL_SERVER", False)
    MAIL_PORT = os.environ.get("HUBGREP_MAIL_PORT", False)
    MAIL_USE_TLS = os.environ.get("HUBGREP_MAIL_USE_TLS", False)
    MAIL_USE_SSL = os.environ.get("HUBGREP_MAIL_USE_SSL", False)
    MAIL_USERNAME = os.environ.get("HUBGREP_MAIL_USERNAME", False)
    MAIL_PASSWORD = os.environ.get("HUBGREP_MAIL_PASSWORD", None)
    MAIL_DEFAULT_SENDER = os.environ.get("HUBGREP_MAIL_DEFAULT_SENDER", None)
    MAIL_MAX_EMAILS = os.environ.get("HUBGREP_MAIL_MAX_EMAILS", None)

    ABOUT_MARKDOWN_FILE = os.environ.get(
        "HUBGREP_ABOUT_MARKDOWN_FILE", "hubgrep_about.md"
    )

    CONTACT_DESCRIPTION = os.environ.get("HUBGREP_CONTACT_DESCRIPTION", None)
    CONTACT_ADDRESS = os.environ.get("HUBGREP_CONTACT_ADDRESS", None)
    CONTACT_EMAIL = os.environ.get("HUBGREP_CONTACT_EMAIL", None)
    CONTACT_PHONE = os.environ.get("HUBGREP_CONTACT_PHONE", None)

    SQLALCHEMY_DATABASE_URI = os.environ.get("HUBGREP_SQLALCHEMY_DATABASE_URI", False)
    SECURITY_PASSWORD_SALT = os.environ.get("HUBGREP_SECURITY_PASSWORD_SALT", False)
    SECRET_KEY = os.environ.get("HUBGREP_SECRET_KEY", False)

    INDEXER_URL = os.environ.get("HUBGREP_INDEXER_URL", None)
    MANTICORE_HOST = os.environ.get("HUBGREP_MANTICORE_HOST", None)


class ProductionConfig(Config, _EnvironmentConfig):
    """Production Configuration."""

    DEBUG = False


class DevelopmentConfig(Config, _EnvironmentConfig):
    """Development configuration."""

    DEBUG = True
    WATCH_SCSS = True


class BuildConfig(Config):
    """Build configuration, in bundling and preparation for deployment."""

    TESTING = True
    DEBUG = True
    SECURITY_SEND_REGISTER_EMAIL = False

    CSS_OUTPUT_STYLE = "compressed"

    MAIL_DEBUG = False

    SQLALCHEMY_DATABASE_URI = ""
    SECURITY_PASSWORD_SALT = ""
    SECRET_KEY = ""
    MANTICORE_HOST = ""


class TestingConfig(Config):
    """Test configuration, as used by tests."""

    TESTING = True
    DEBUG = True
    SECURITY_SEND_REGISTER_EMAIL = False

    MAIL_DEBUG = False

    SQLALCHEMY_DATABASE_URI = ""
    SECURITY_PASSWORD_SALT = ""
    SECRET_KEY = ""
    ABOUT_MARKDOWN_FILE = "hubgrep_about.md"

    CONTACT_DESCRIPTION = None
    CONTACT_ADDRESS = None
    CONTACT_EMAIL = None
    CONTACT_PHONE = None
    MANTICORE_HOST = None

    SQLALCHEMY_DATABASE_URI = "postgresql://hubgrep:hubgrep@test_postgres:5432/hubgrep"
