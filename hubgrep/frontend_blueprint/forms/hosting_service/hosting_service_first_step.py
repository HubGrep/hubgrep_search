import logging

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.widgets.html5 import URLInput
from wtforms.validators import URL
from wtforms.validators import InputRequired


logger = logging.getLogger(__name__)


class HostingServiceFormFirstStep(FlaskForm):
    """ Only get type and landingpage from the user, the rest we automatically resolve to pre-fill in step 2. """

    type = SelectField(
        u"Type",
        [InputRequired()],
        choices=[
            ("gitea", "gitea"),
            ("gitlab", "Gitlab"),
            ("github", "GitHub"),
        ],
    )
    landingpage_url = StringField(
        "Landingpage Url",
        [InputRequired(), URL()],
        widget=URLInput(),
    )
