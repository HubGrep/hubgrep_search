import logging
from flask_wtf import FlaskForm


logger = logging.getLogger(__name__)


class ConfirmForm(FlaskForm):
    """
    empty "confirm" form
    """
    pass
