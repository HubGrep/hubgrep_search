"""
HubGrep retrieves results from external hosting-services (such as GitHub, or GitLab). This is done via these interfaces.
"""

from hubgrep.lib.hosting_service_interfaces.github import GitHubSearch
from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch
from hubgrep.lib.hosting_service_interfaces.gitlab import GitLabSearch
from hubgrep.lib.hosting_service_interfaces.sphinx import SphinxSearch

hosting_service_interface_mapping = dict(
    github=GitHubSearch, gitlab=GitLabSearch, gitea=GiteaSearch, sphinx=SphinxSearch
)

