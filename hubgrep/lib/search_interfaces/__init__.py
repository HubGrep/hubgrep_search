from hubgrep.lib.search_interfaces.github import GitHubSearch
from hubgrep.lib.search_interfaces.gitea import GiteaSearch
from hubgrep.lib.search_interfaces.gitlab import GitLabSearch

search_interfaces_by_name = dict(
    github=GitHubSearch, gitlab=GitLabSearch, gitea=GiteaSearch
)
