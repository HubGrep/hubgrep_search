""" HubGrep constants """

from flask_babel import gettext

# app
APP_ENV_BUILD = "build"
APP_ENV_DEVELOPMENT = "development"
APP_ENV_PRODUCTION = "production"
APP_ENV_TESTING = "testing"

DATE_FORMAT = "%Y-%m-%d"

# hosting services
HOSTING_SERVICE_REQUEST_TIMEOUT_DEFAULT = 2

# pagination
PARAM_OFFSET = "offset"
PARAM_PER_PAGE = "per_page"
CLASS_CURRENT_PAGE = "current-page"
CLASS_PREV = "prev"
CLASS_NEXT = "next"
CLASS_DIVIDER = "divider"

# hoster errors
UNKNOWN_ERROR = -1
CONNECTION_ERROR = -2
TIMEOUT_ERROR = -3
TOO_MANY_REDIRECTS_ERROR = -4


# search form
class FORM_ARGS:
    search_phrase = "s"
    exclude_forks = "f"
    exclude_archived = "a"
    exclude_mirror = "m"
    exclude_empty = "e"
    created_after = "ca"
    created_before = "cb"
    updated_after = "ua"
    pushed_after = "pa"


# frontend
SITE_TITLE = "HubGrep"
REPO_CREATED = "created"
REPO_MODIFIED = "modified"

TOOLTIP_REPO_CREATED_AT = gettext("Date and time when a repository was created.")
TOOLTIP_REPO_MODIFIED_AT = gettext("Date and time when a repository was modified - possibly not via push.")
TOOLTIP_REPO_PUSHED_AT = gettext("Date and time of the last push to a repository.")
TOOLTIP_REPO_LANGUAGE = gettext("Majority used language.")
TOOLTIP_REPO_LICENSE = gettext("License in use by a repository.")
TOOLTIP_REPO_WEIGHT = gettext("HubGreps score of how relevant an repository is to your search-phrase.")
TOOLTIP_REPO_AGE = gettext("How old the repository is.")

TOOLTIP_FILTER_CREATED_BEFORE = gettext("Only include repositories that were created before this date.")
TOOLTIP_FILTER_CREATED_AFTER = gettext("Only include repositories that were created after this date.")
TOOLTIP_FILTER_MODIFIED_SINCE = gettext(
    "Only include repositories that were modified after this date. Note that modified does not necessarily mean via push.")
TOOLTIP_FILTER_PUSHED_SINCE = gettext("Only include repositories that have commits made to it after this date.")
TOOLTIP_FILTER_EXCLUDE_SOURCE = gettext("Remove all repositories from results which belong to a hosting service.")
TOOLTIP_FILTER_EXCLUDE_FORK = gettext("Remove all repositories which are forks from search results.")
TOOLTIP_FILTER_EXCLUDE_ARCHIVED = gettext("Remove all repositories which are archived from search results.")
TOOLTIP_FILTER_EXCLUDE_MIRROR = gettext("Remove all repositories which are mirrors from search results.")
TOOLTIP_FILTER_EXCLUDE_EMPTY = gettext("Remove all empty repositories from search results.")
TOOLTIP_TAG_FORK = gettext("This repository is a fork.")
TOOLTIP_TAG_ARCHIVED = gettext("This repository has been archived.")
TOOLTIP_TAG_MIRROR = gettext("This repository is a mirror - visit repo page to find original.")
TOOLTIP_TAG_EMPTY = gettext("This repository has no content, only meta-data.")

MISSING_VALUE_DEFAULT = "—"

SEARCH_HINTS = [
    {
        "prefix": gettext("exact match:"),
        "highlight": "\"alice carrol\"",
        "suffix": gettext("Get results containing exact matches.")
    },
    {
        "prefix": gettext("search by field:"),
        "highlight": "alice @username carrol",
        "suffix": gettext("Only carrol is matched against username.")
    },
    {
        "prefix": gettext("exclude a word:"),
        "highlight": "alice !wonderland",
        "suffix": gettext("Only match results containing alice, but not if they also contain wonderland.")
    },
    {
        "prefix": gettext("alternative search:"),
        "highlight": "alice | wonderland",
        "suffix": gettext("Will match results containing either alice OR wonderland.")
    },
    {
        "prefix": gettext("preferential search:"),
        "highlight": "alice MAYBE wonderland",
        "suffix": gettext("Will mainly search for alice, but boost matches containing wonderland.")
    },
]
