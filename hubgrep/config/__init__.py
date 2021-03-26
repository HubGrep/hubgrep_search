import os


class Config:
    # user defined config
    ENABLE_CACHE = os.environ.get("HUBGREP_ENABLE_CACHE", True)
    CACHE_TIME = os.environ.get("HUBGREP_CACHE_TIME", 3600)
    REDIS_URL = os.environ["HUBGREP_REDIS_URL"]

    MAIL_DEBUG = os.environ.get('HUBGREP_MAIL_DEBUG', False)

    MAIL_SERVER = os.environ['HUBGREP_MAIL_SERVER']
    MAIL_PORT = os.environ['HUBGREP_MAIL_PORT']
    MAIL_USE_TLS = os.environ.get('HUBGREP_MAIL_USE_TLS', False)
    MAIL_USE_SSL = os.environ.get('HUBGREP_MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('HUBGREP_MAIL_USERNAME', False)
    MAIL_PASSWORD = os.environ.get('HUBGREP_MAIL_PASSWORD', None)
    MAIL_DEFAULT_SENDER = os.environ.get('HUBGREP_MAIL_DEFAULT_SENDER', None)
    MAIL_MAX_EMAILS = os.environ.get('HUBGREP_MAIL_MAX_EMAILS', None)


    SQLALCHEMY_DATABASE_URI = os.environ["HUBGREP_SQLALCHEMY_DATABASE_URI"]
    SECURITY_PASSWORD_SALT = os.environ["HUBGREP_SECURITY_PASSWORD_SALT"]
    SECRET_KEY = os.environ["HUBGREP_SECRET_KEY"]


    # hardcoded config
    DEBUG = False
    TESTING = False
    LOGLEVEL = "debug"
    VERSION = "0.0.0"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BABEL_DEFAULT_LOCALE = "en"
    BABEL_DEFAULT_TIMEZONE = "UTC"
    LANGUAGES = {"en": "English", "de": "Deutsch"}

    # https://flask-security-too.readthedocs.io/en/stable/configuration.html
    SECURITY_LOGIN_URL = "/login"
    SECURITY_LOGOUT_URL = "/logout"
    SECURITY_POST_LOGIN_VIEW = "/"
    SECURITY_POST_LOGOUT_VIEW = "/"
    SECURITY_LOGIN_USER_TEMPLATE = "security/login_user.html"

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    SECURITY_EMAIL_SUBJECT_REGISTER = "Welcome"
    SECURITY_REGISTER_USER_TEMPLATE = "security/register_user.html"
    SECURITY_REGISTER_URL = "/register"

    SECURITY_CONFIRMABLE = True
    SECURITY_SEND_CONFIRMATION_TEMPLATE = "security/send_confirmation.html"

    SECURITY_RECOVERABLE = True
    SECURITY_RESET_URL = "/reset"
    SECURITY_RESET_PASSWORD_TEMPLATE = "security/reset_password.html"
    SECURITY_FORGOT_PASSWORD_TEMPLATE = "security/forgot_password.html"


    PAGINATION_PER_PAGE_DEFAULT = 10


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SECURITY_SEND_REGISTER_EMAIL = False
