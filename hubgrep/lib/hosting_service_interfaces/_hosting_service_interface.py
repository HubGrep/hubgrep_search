"""
Base-classes for search results and hosting-service interfaces.
"""

import logging
import time
import click
import humanize
import requests
import pytz

from typing import List
from urllib.parse import urljoin
from flask import current_app

from hubgrep.lib.cached_session.cached_session import CachedSession
from hubgrep.lib.cached_session.cached_response import CachedResponse
from hubgrep.constants import UNKNOWN_ERROR, CONNECTION_ERROR, TIMEOUT_ERROR, TOO_MANY_REDIRECTS_ERROR

logger = logging.getLogger(__name__)

utc = pytz.UTC


class SearchResult:
    """ A single repository result as retrieved by all hosting-service interfaces """

    def __init__(
        self,
        host_service_id,
        repo_name,
        repo_description,
        html_url,
        owner_name,
        last_commit_dt,
        created_at_dt,
        forks,
        stars,
        is_fork,
        is_archived,
        language=None,
        license=None,
    ):
        self.host_service_id = host_service_id
        self.repo_name = repo_name
        self.repo_description = repo_description
        self.html_url = html_url
        self.owner_name = owner_name
        self.last_commit_dt = last_commit_dt.astimezone(pytz.utc)
        self.last_commit = humanize.naturaldate(last_commit_dt)
        self.created_at_dt = created_at_dt.astimezone(pytz.utc)
        self.created_at = humanize.naturaldate(created_at_dt)
        self.language = language
        self.license = license

        self.forks = forks
        self.stars = stars
        self.is_fork = is_fork
        self.is_archived = is_archived

        self.score = -1  # score we calculate after fetching

        self.text = ""

    def _append_to_print(self, key, value):
        self.text += click.style(key, bold=True)
        self.text += f"{value}\n"

    def get_cli_formatted(self) -> str:
        """ Format output for a CLI as a target. """
        self.last_commit = self.last_commit_dt.replace(tzinfo=None)
        self.created_at = self.created_at_dt.replace(tzinfo=None)
        last_commit = humanize.naturaltime(self.last_commit)
        created_at = humanize.naturaltime(self.created_at)

        self._append_to_print(f"{self.owner_name} / {self.repo_name}", "")
        self._append_to_print("  Last commit: ", last_commit)
        self._append_to_print("  Created: ", created_at)
        self._append_to_print("  -> ", self.html_url)
        self._append_to_print("  Description: ", self.repo_description[:100])
        self._append_to_print("  Language: ", self.language)
        self._append_to_print("  fork: ", self.is_fork)
        self._append_to_print("  archived: ", self.is_archived)

        self._append_to_print("  Score: ", self.score)

        return self.text


class HostingServiceInterface:
    """ Hosting-service interface base-class. """

    name = ""

    def __init__(
        self,
        host_service_id,
        api_url,
        search_path,
        label,
        config_dict,
        cached_session: CachedSession,
        timeout=None,
    ):
        self.host_service_id = host_service_id
        self.api_url = api_url
        self.label = label
        self.config_dict = config_dict
        self.request_url = urljoin(self.api_url, search_path)
        self.timeout = timeout
        self.cached_session = cached_session
        self.cached_session.headers.update({"referer": current_app.config["REFERER"]})

    def search(
        self, keywords: list = [], tags: dict = {}
    ) -> "HostingServiceInterfaceResponse":
        """ Send a request to an external hosting-service to retrieve search results. """
        time_before = time.time()
        hosting_service_interface_result = self._search(keywords, tags)
        logger.debug(f"search on {self.api_url} took {time.time() - time_before}s")
        return hosting_service_interface_result

    def _search(self, keywords: list, tags: dict) -> "HostingServiceInterfaceResponse":
        raise NotImplementedError

    def _get_request_headers(self) -> dict:
        return dict()

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        """ Define a default api_url as derived from a landingpage_url - for autocomplete convenience."""
        return NotImplementedError

    @staticmethod
    def normalize_url(url) -> str:
        response = requests.head(url)
        return response.url


class HostingServiceInterfaceResponse:
    """
    Wrapper class containing a hosting_interface,
    the interfaces response and potential search results.

    Used in the search jinja templates.
    """

    hosting_service_interface: HostingServiceInterface
    response: CachedResponse
    search_results: List[SearchResult]

    def __init__(
        self,
        hosting_service_interface: HostingServiceInterface,
        response: CachedResponse,
        search_results: List[SearchResult],
    ):
        self.hosting_service_interface = hosting_service_interface
        self.response = response
        self.search_results = search_results

    @property
    def succeeded(self) -> bool:
        return self.response.success

    def get_admin_error_message(self):
        prefix = f"There was a problem retrieving results from {self.hosting_service_interface.label} ({self.response.status_code}):"
        return f"{prefix} {self.response.error_msg}"

    def get_user_error_message(self):
        """
        get an error message to display to a user.
        """

        prefix = f"There was a problem retrieving results from {self.hosting_service_interface.label}:"

        if self.response.status_code == TOO_MANY_REDIRECTS_ERROR:
            return f"{prefix} Too many redirects"
        elif self.response.status_code == CONNECTION_ERROR:
            return f"{prefix} Connection error"
        elif self.response.status_code == TIMEOUT_ERROR:
            return f"{prefix} Took too long"
        elif self.response.status_code == UNKNOWN_ERROR:
            return f"{prefix} Unknown error"

        elif 400 <= self.response.status_code <= 499:
            return f"{prefix} Client error"
        elif 500 <= self.response.status_code <= 599:
            return f"{prefix} Server error"
        else:
            return f"{prefix} Unknown error"
