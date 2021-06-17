import json
import logging

import markdown

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.widgets.html5 import URLInput
from wtforms.validators import ValidationError, URL
from wtforms.validators import InputRequired

from hubgrep.lib.hosting_service_interfaces import hosting_service_interface_mapping
from hubgrep.models import HostingService

logger = logging.getLogger(__name__)


def validate_custom_config(form, field):
    """ Validate the config field to adhere to JSON syntax. """
    if not field.data:
        field.data = "{}"
    try:
        config = json.loads(field.data)
        field.data = json.dumps(config, sort_keys=True)
    except Exception:
        raise ValidationError("Config must be valid json")


def validate_url(form, field):
    HostingServiceInterface = hosting_service_interface_mapping.get(
        form.type.data, False
    )
    """ Validate URLs. """
    if not HostingServiceInterface:
        raise ValidationError("invalid hosting service interface!")
    field.data = HostingServiceInterface.normalize_url(field.data)


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
        [InputRequired(), URL(), validate_url],
        widget=URLInput(),
    )


class NoHostingServiceFormException(Exception):
    pass

class HostingServiceForm(HostingServiceFormFirstStep):
    """ Final step when adding a new hosting-service, doubling as the form used for editing hosting-services. """

    api_url = StringField(
        "Api Url", [InputRequired(), URL(), validate_url], widget=URLInput()
    )
    custom_config = TextAreaField(
        "Custom config",
        [validate_custom_config],
        description="Custom config json. If you dont know what to put in, just leave it empty. :)",
    )
    help_text_md = ""

    def populate_api_url(self):
        self.api_url.data = self.landingpage_url.data

    def to_hosting_service(self):
        """
        create hosting service (the db model, not the interface) from form data
        """
        h = HostingService()

        # set current_user later - this should be request-agnostic :)
        h.user_id = None

        h.api_url = self.api_url.data
        h.landingpage_url = self.landingpage_url.data
        h.type = self.type.data
        if hasattr(self, "api_key"):
            h.api_key = self.api_key.data
        else:
            h.api_key = None
        h.custom_config = self.custom_config.data
        h.set_service_label()
        return h

    @classmethod
    def from_hosting_service_type(cls, hoster_type: str):
        hosting_service_forms_mapping = dict(
            github=GithubHostingServiceForm,
            gitlab=GitlabHostingServiceForm,
            gitea=GiteaHostingServiceForm,
        )

        Form = hosting_service_forms_mapping.get(hoster_type, False)
        if not Form:
            raise NoHostingServiceFormException("No form found to edit {hosting_service.type}")
        return Form()

    @classmethod
    def from_hosting_service(cls, hosting_service: HostingService):
        """
        create new form from hosting_service data
        """
        form = cls.from_hosting_service_type(hosting_service.type)

        form.type.data = hosting_service.type
        form.landingpage_url.data = hosting_service.landingpage_url
        form.api_url.data = hosting_service.api_url
        if hasattr(form, "api_key"):
            form.api_key.data = hosting_service.api_key
        form.custom_config.data = hosting_service.custom_config
        return form

    @property
    def help_text_html(self):
        return markdown.markdown(self.help_text_md)


class ApiKeyHostingServiceForm(HostingServiceForm):
    api_key = StringField("Api Key*")
    help_text_md = ""


class GithubHostingServiceForm(ApiKeyHostingServiceForm):
    help_text_md = """
> todo: how to get a gh api key
    """


class GitlabHostingServiceForm(ApiKeyHostingServiceForm):
    """
    gitlab detail form.
    gitlab needs an api key, and a help text...
    """
    help_text_md = """
*Gitlab needs an API Key (“token”) to use the api.

> **! Keep in mind, that with this token, your private repositories can be read as well,**
> **so its recommended to create a new, empty user account for this !**

To create a new token:

- log in to your Gitlab account
- find “access tokens” in your user settings
- create a new “personal access token” without an expiration date, and with the `read_api` scope.

if you ever feel like we should not have this token, you can revoke it there as well.
    """


class GiteaHostingServiceForm(HostingServiceForm):
    """
    gitea detail form. nothing to see here. doesnt need anything. :)
    """
    pass
