from hubgrep.lib.hosting_service_interfaces.github import GitHubSearch
from hubgrep.lib.hosting_service_interfaces.gitea import GiteaSearch
from hubgrep.lib.hosting_service_interfaces.gitlab import GitLabSearch


hosting_service_interface_mapping = dict(
    github=GitHubSearch, gitlab=GitLabSearch, gitea=GiteaSearch
)

