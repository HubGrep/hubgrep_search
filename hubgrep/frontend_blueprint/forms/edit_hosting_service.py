from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextField
from wtforms.widgets.html5 import URLInput
from wtforms.validators import DataRequired, ValidationError , URL

import json

def validate_config(form, field):
    if not field.data:
        field.data = '{}'
    try:
        config = json.loads(field.data)
        field.data = json.dumps(config, sort_keys=True)
    except Exception:
        raise ValidationError('Config must be valid json')

    if form.type.data == 'gitlab':
        if not 'api_token' in config.keys():
            raise ValidationError('GitLab needs an API token in config, like \'{"api_token": "XXXXX"}\'')


class HostingServiceForm(FlaskForm):
    type = SelectField(
        u"Type",
        choices=[
            ("gitea", "gitea"),
            ("gitlab", "Gitlab"),
            ("github", "GitHub"),
        ],
    )
    frontpage_url = StringField("Frontpage Url", [URL()], widget=URLInput())
    base_url = StringField("Api Url", [URL()], widget=URLInput())
    config = TextField("Config", [validate_config])
