from datetime import datetime
from urllib.parse import urljoin

import click
import humanize
import requests


class SearchResult:
    def __init__(
        self,
        repo_name,
        repo_description,
        html_url,
        owner_name,
        last_commit,
        created_at,
        forks,
        stars,
        is_fork,
        is_archived,
        language=None,
        license=None,
    ):
        self.repo_name = repo_name
        self.repo_description = repo_description
        self.html_url = html_url
        self.owner_name = owner_name
        self.last_commit_raw = last_commit
        self.last_commit = humanize.naturaldate(last_commit)
        self.created_at_raw = created_at
        self.created_at = humanize.naturaldate(created_at)
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

    def get_cli_formatted(self):
        self.last_commit = self.last_commit_raw.replace(tzinfo=None)
        self.created_at = self.created_at_raw.replace(tzinfo=None)
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
    name = ""

    def __init__(self, base_url, search_path, requests_session=None):
        self.base_url = base_url
        self.request_url = urljoin(self.base_url, search_path)

        if requests_session:
            self.requests = requests_session
        else:
            self.requests = requests.session()

    def search(self, keywords: list, tags: dict):
        raise NotImplementedError
