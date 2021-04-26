import json
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextField, TextAreaField
from wtforms.widgets.html5 import URLInput
from wtforms.validators import DataRequired, ValidationError, URL
from wtforms.validators import InputRequired

from hubgrep.lib.hosting_service_interfaces import hosting_service_interface_mapping

logger = logging.getLogger(__name__)


def validate_config(form, field):
    if not field.data:
        field.data = "{}"
    try:
        config = json.loads(field.data)
        field.data = json.dumps(config, sort_keys=True)
    except Exception:
        raise ValidationError("Config must be valid json")

    if form.type.data == "gitlab":
        if not "api_token" in config.keys():
            raise ValidationError(
                'GitLab needs an API token in config, like \'{"api_token": "XXXXX"}\''
            )

def validate_url(form, field):
    HostingServiceInterface = hosting_service_interface_mapping.get(form.type.data, False)
    if not HostingServiceInterface:
        raise ValidationError("invalid hosting service interface!")
    field.data = HostingServiceInterface.normalize_url(field.data)


class HostingServiceFirstStep(FlaskForm):
    """
    only get type and landingpage from user,
    we want to figure out the rest to prefill step 2
    """
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
        [
            InputRequired(),
            URL(),
            validate_url
        ],
        widget=URLInput(),
    )

class HostingServiceForm(HostingServiceFirstStep):
    """
    final step in adding new hosters,
    also form for editing hosters
    """
    api_url = StringField("Api Url", [InputRequired(), URL(), validate_url], widget=URLInput())
    config = TextAreaField("Config", [validate_config])

    def populate_api_url(self):
        HostingServiceInterface = hosting_service_interface_mapping.get(self.type.data, False)
        if not HostingServiceInterface:
            logger.error('hosting interface for "{form.type.data}" not found!')
            return
        api_url = HostingServiceInterface.default_api_url_from_landingpage_url(self.landingpage_url.data)
        self.api_url.data = api_url


