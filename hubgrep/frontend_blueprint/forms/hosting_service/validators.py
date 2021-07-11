"""
validator functions for the form fields
"""
import json
from wtforms.validators import ValidationError


def validate_custom_config(form, field):
    """ Validate the config field to adhere to JSON syntax. """
    if not field.data:
        field.data = "{}"
    try:
        config = json.loads(field.data)
        field.data = json.dumps(config, sort_keys=True)
    except Exception:
        raise ValidationError("Config must be valid json")

