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

        h.api_url = self.api_url.data
        h.landingpage_url = self.landingpage_url.data
        h.type = self.type.data
        if hasattr(self, "api_key"):
            h.api_key = self.api_key.data
        else:
            h.api_key = None
        h.custom_config = self.custom_config.data
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

    @property
    def important_notes_html(self):
        return markdown.markdown(self.important_notes_md)


class ApiKeyHostingServiceForm(HostingServiceForm):
    api_key = StringField("Api Key*")
    important_notes_md = ""


class GithubHostingServiceForm(ApiKeyHostingServiceForm):
    """
    github detail form.
    """
    important_notes_md = ""


class GitlabHostingServiceForm(HostingServiceForm):
    """
    gitlab detail form.
    """

    important_notes_md = ""


class GiteaHostingServiceForm(HostingServiceForm):
    """
    gitea detail form.
    """
