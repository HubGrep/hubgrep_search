import json
import logging

import markdown

from wtforms import StringField, TextAreaField
from wtforms.widgets.html5 import URLInput
from wtforms.validators import URL
from wtforms.validators import InputRequired

from hubgrep.models import HostingService

from hubgrep.frontend_blueprint.forms.hosting_service.validators import (
    validate_custom_config,
)

from hubgrep.frontend_blueprint.forms.hosting_service.hosting_service_first_step import HostingServiceFormFirstStep

logger = logging.getLogger(__name__)


class NoHostingServiceFormException(Exception):
    pass

class HostingServiceForm(HostingServiceFormFirstStep):
    """ Final step when adding a new hosting-service, doubling as the form used for editing hosting-services. """

    # validate_url sanitizes url before validate_api_url makes a call to it
    api_url = StringField(
        "Api Url",
        [InputRequired(), URL()],
        widget=URLInput(),
        description="should be the same as the landing page in most cases"
    )
    custom_config = TextAreaField(
        "Custom config",
        [validate_custom_config],
        description="Custom config json. If you dont know what to put in, just leave it empty.",
    )
    important_notes_md = ""

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
        """
        make a form for a sepecfic hoster type
        """
        hosting_service_forms_mapping = dict(
            github=GithubHostingServiceForm,
            gitlab=GitlabHostingServiceForm,
            gitea=GiteaHostingServiceForm,
        )

        Form = hosting_service_forms_mapping.get(hoster_type, False)
        if not Form:
            raise NoHostingServiceFormException(
                "No form found to edit {hosting_service.type}"
            )
        return Form()

    @classmethod
    def from_hosting_service(cls, hosting_service: HostingService):
        """
        create new form from hosting_service data
        (prefills the form data)
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
    def important_notes_html(self):
        return markdown.markdown(self.important_notes_md)


class ApiKeyHostingServiceForm(HostingServiceForm):
    api_key = StringField("Api Key*")
    important_notes_md = ""


class GithubHostingServiceForm(ApiKeyHostingServiceForm):
    important_notes_md = ""


class GitlabHostingServiceForm(ApiKeyHostingServiceForm):
    """
    gitlab detail form.
    gitlab needs an api key, and a help text...
    """

    important_notes_md = """
*Gitlab needs an API Key (“token”) to use the search api.

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
    gitea detail form.
    """
