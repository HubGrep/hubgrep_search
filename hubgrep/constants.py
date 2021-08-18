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

TOOLTIP_REPO_CREATED_AT = "Date and time when a repository was created."
TOOLTIP_REPO_MODIFIED_AT = "Date and time when a repository was modified - possibly not via push."
TOOLTIP_REPO_PUSHED_AT = "Date and time of the last push to a repository."
TOOLTIP_REPO_LANGUAGE = "Majority used language."
TOOLTIP_REPO_LICENSE = "License in use by a repository."
TOOLTIP_REPO_WEIGHT = "HubGreps score of how relevant an repository is to your search-phrase."
TOOLTIP_REPO_AGE = "How old the repository is."

TOOLTIP_FILTER_CREATED_BEFORE = "Only include repositories that were created before this date."
TOOLTIP_FILTER_CREATED_AFTER = "Only include repositories that were created after this date."
TOOLTIP_FILTER_MODIFIED_SINCE = "Only include repositories that were modified after this date. Note that modified does not necessarily mean via push."
TOOLTIP_FILTER_PUSHED_SINCE = "Only include repositories that have commits made to it after this date."
TOOLTIP_FILTER_EXCLUDE_FORK = "Remove all repositories which are forks from search results."
TOOLTIP_FILTER_EXCLUDE_ARCHIVED = "Remove all repositories which are archived from search results."
TOOLTIP_FILTER_EXCLUDE_MIRROR = "Remove all repositories which are mirrors from search results."
TOOLTIP_FILTER_EXCLUDE_SOURCE = "Remove all repositories from results which belong to a hosting service."

MISSING_VALUE_DEFAULT = "—"
