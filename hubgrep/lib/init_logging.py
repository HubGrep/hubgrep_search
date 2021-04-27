""" Logging initialization with defaults. """

from logging.config import dictConfig


def init_logging(loglevel="info"):
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": "%(asctime)s %(name)s [%(levelname)s]: %(message)s"},
            },
            "handlers": {
                "default": {
                    "level": loglevel.upper(),
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": loglevel.upper(),
                    "propagate": True,
                },
                "boto3": {
                    "level": "CRITICAL",
                },
                "botocore": {
                    "level": "CRITICAL",
                },
                "s3transfer": {
                    "level": "CRITICAL",
                },
                "urllib3": {
                    "level": "CRITICAL",
                },
                "passlib.registry": {
                    "level": "INFO",
                },
            },
        }
    )
