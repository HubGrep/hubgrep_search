from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextField
from wtforms.widgets.html5 import URLInput
from wtforms.validators import DataRequired


class HostingServiceForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    type = SelectField(
        u"Type",
        choices=[
            ("gitea", "gitea"),
            ("gitlab", "Gitlab"),
            ("github", "GitHub"),
        ],
    )
    frontpage_url = StringField("Frontpage Url", widget=URLInput())
    base_url = StringField("Api Url", widget=URLInput())
    config = TextField("Config")
