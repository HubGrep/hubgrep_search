""" HubGrep constants """

# app
APP_ENV_BUILD = "build"
APP_ENV_DEVELOPMENT = "development"
APP_ENV_PRODUCTION = "production"
APP_ENV_TESTING = "testing"

# hosting services
HOSTING_SERVICE_REQUEST_TIMEOUT_DEFAULT = 2

# search form


# pagination
PARAM_OFFSET = "offset"
PARAM_PER_PAGE = "per_page"
CLASS_CURRENT_PAGE = "current-page"
CLASS_PREV = "prev"
CLASS_NEXT = "next"
CLASS_DIVIDER = "divider"


# search form
DATE_FORMAT = "%Y-%m-%d"

# hoster errors
UNKNOWN_ERROR = -1
CONNECTION_ERROR = -2
TIMEOUT_ERROR = -3
TOO_MANY_REDIRECTS_ERROR = -4


class FORM_ARGS:
    search_phrase = "s"
    exclude_forks = "f"
    exclude_archived = "a"
    exclude_disabled = "d"
    exclude_mirror = "m"
    created_after = "ca"
    created_before = "cb"
    updated_after = "ua"


# frontend
SITE_TITLE = "HubGrep"
REPO_CREATED = "created"
REPO_MODIFIED = "modified"

TOOLTIP_FILTER_CREATED_AT = "Repository was created at this date."
TOOLTIP_FILTER_MODIFIED_AT = "Repository was updated at this date - possibly not via push."
TOOLTIP_FILTER_PUSHED_AT = "Repository was last pushed to at this date."
TOOLTIP_FILTER_LANGUAGE = "Majority used language."
TOOLTIP_FILTER_LICENSE = "License used by this project."
TOOLTIP_FILTER_WEIGHT = "HubGreps score of how relevant this item is to your search-phrase."
TOOLTIP_FILTER_AGE = "How old the repository is."

MISSING_VALUE_DEFAULT = "—"
