from datetime import timedelta
from hubgrep.lib.hosting_service_interfaces.github import GitHubSearchResult
from hubgrep.lib.hosting_service_interfaces.gitlab import GitLabSearchResult
from hubgrep.lib.search_form import SearchForm, Checkbox
from hubgrep.lib.filter_results import filter_results

GH_NAME = 'test_github'
GH_CREATED = '2000-01-01T00:00:00Z'
GH_UPDATED = '2010-01-01T00:00:00Z'
GL_NAME = 'test_gitlab'
GL_CREATED = '2015-01-01T00:00:00Z'
GL_UPDATED = '2020-01-01T00:00:00Z'
UNI_RESULT = {'name': 'this mock should work for both GitHubSearchResult and GitLabSearchResult',
              'owner': {'login': 'test_gh_person'},
              "namespace": {"path": 'test_gl_person'},
              'html_url': 'test_url',
              'http_url_to_repo': 'test_url',
              'description': 'test_desc',
              'created_at': '1970-01-01T00:00:00Z',
              'updated_at': GH_UPDATED,
              'last_activity_at': GL_UPDATED,
              'archived': False,
              'fork': False,
              'forks_count': 1,
              'stargazers_count': 1,
              'star_count': 1,
              'language': None,
              'license': {'name': 'test_license'}}
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


class TestFilterResults:

    @staticmethod
    def _get_form_mock(gh_checked: bool = False, gl_checked: bool = False):
        checkboxes = {"gh": Checkbox("gh", 1, "github", gh_checked),
                      "gl": Checkbox("gl", 1, "gitlab", gl_checked)}
        return SearchForm(search_phrase="irrelevant",
                          exclude_service_checkboxes=checkboxes)

    @staticmethod
    def _get_results_mock():
        # give me 2 items, 1 github & 1 gitlab, with defaults
        gh_res = UNI_RESULT.copy()
        gh_res["name"] = GH_NAME
        gh_res["created_at"] = GH_CREATED
        gl_res = UNI_RESULT.copy()
        gl_res["name"] = GL_NAME
        gl_res["created_at"] = GL_CREATED
        return [GitHubSearchResult(gh_res, "gh"), GitLabSearchResult(gl_res, "gl")]

    def test_filter_forks(self):
        results = self._get_results_mock()
        form = self._get_form_mock()
        form.exclude_forks = True
        results[0].is_fork = True  # test_github should be filtered out
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 1
        assert filter_res[0].repo_name == GL_NAME

    def test_filter_archived(self):
        results = self._get_results_mock()
        form = self._get_form_mock()
        form.exclude_archived = True
        results[1].is_archived = True  # test_gitlab should be filtered out
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 1
        assert filter_res[0].repo_name == GH_NAME

    def test_filter_created_before(self):
        results = self._get_results_mock()
        form = self._get_form_mock()
        date = SearchForm.get_form_datetime_in_utc(GL_CREATED, DATE_FORMAT) - timedelta(days=1)
        form.created_before_dt = date  # test_gitlab should be filtered out
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 1
        assert filter_res[0].repo_name == GH_NAME

    def test_filter_created_after(self):
        results = self._get_results_mock()
        form = self._get_form_mock()
        date = SearchForm.get_form_datetime_in_utc(GL_CREATED, DATE_FORMAT) - timedelta(days=1)
        form.created_after_dt = date  # test_github should be filtered out
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 1
        assert filter_res[0].repo_name == GL_NAME

    def test_filter_updated_after(self):
        results = self._get_results_mock()
        form = self._get_form_mock()
        date = SearchForm.get_form_datetime_in_utc(GL_UPDATED, DATE_FORMAT) - timedelta(days=1)
        form.updated_after_dt = date  # test_github should be filtered out
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 1
        assert filter_res[0].repo_name == GL_NAME

    def test_filter_host_services(self):
        results = self._get_results_mock()
        form = self._get_form_mock(gl_checked=True)  # test_gitlab should be filtered out
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 1
        assert filter_res[0].repo_name == GH_NAME

    def test_exclude_nothing(self):
        results = self._get_results_mock()
        form = self._get_form_mock()
        form.exclude_forks = False
        form.exclude_archived = False
        form.created_before_dt = form.get_form_datetime_in_utc("2100-01-01")
        form.created_after_dt = form.get_form_datetime_in_utc("1970-01-01")
        form.updated_after_dt = form.get_form_datetime_in_utc("1970-01-01")
        filter_res = filter_results(results=results, form=form)
        assert len(filter_res) == 2
