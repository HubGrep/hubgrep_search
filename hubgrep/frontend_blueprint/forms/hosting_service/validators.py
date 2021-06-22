"""
validator functions for the form fields
"""
import json
from wtforms.validators import ValidationError

from hubgrep.lib.hosting_service_interfaces import hosting_service_interface_mapping


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
    """ Validate and normalize URLs. """
    HostingServiceInterface = hosting_service_interface_mapping.get(
        form.type.data, False
    )
    if not HostingServiceInterface:
        raise ValidationError("invalid hosting service interface!")
    field.data = HostingServiceInterface.normalize_url(field.data)



def validate_api_url(form, field):
    """
    Test validity of this hosting service by sending a request,
    and see if its a response we expect.

    see `test_validity` mehod of each HostingServiceInterface
    """
    from hubgrep.lib.cached_session.caches.no_cache import NoCache
    from hubgrep.lib.cached_session.cached_session import CachedSession
    import requests

    cached_session = CachedSession(requests.Session(), NoCache())

    hosting_service = form.to_hosting_service()
    hosting_service_interface = hosting_service.get_hosting_service_interface(
        cached_session, timeout=5
    )
    if not hosting_service_interface.test_validity():
        raise ValidationError("Hoster did not return a valid response!")
    return True
