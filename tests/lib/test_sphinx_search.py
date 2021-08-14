import datetime
from hubgrep.lib.sphinx import SphinxSearch


class TestSphinxSearch:
    def test_make_bool_filters_empty(self):
        sphinx = SphinxSearch()

        # no bool filters should result in an empty string
        filters = sphinx._make_bool_filters(
            exclude_forks=None,
            exclude_archived=None,
            exclude_disabled=None,
            exclude_mirror=None,
        )
        assert filters == ""

    def test_make_bool_filters_partially(self):
        sphinx = SphinxSearch()
        # no bool filters should result in an empty string
        filters = sphinx._make_bool_filters(
            exclude_forks=True,
            exclude_archived=None,
            exclude_disabled=None,
            exclude_mirror=None,
        )
        # "exclude forks" translates to "is_fork = 0"
        assert filters == "and is_fork = 0"

        filters = sphinx._make_bool_filters(
            exclude_forks=True,
            exclude_archived=None,
            exclude_disabled=True,
            exclude_mirror=None,
        )
        # "exclude forks" translates to "is_fork = false"
        assert filters == "and is_disabled = 0 and is_fork = 0"

    def test_make_sql_time_filter_empty(self):
        sphinx = SphinxSearch()
        time_filter_str, time_filter_vars = sphinx._make_sql_time_filter(
            created_after=None,
            created_before=None,
            updated_after=None,
        )
        assert time_filter_str == ""

    def test_make_sql_time_filter_partially(self):
        sphinx = SphinxSearch()
        timestamp_before = datetime.datetime.fromtimestamp(0)
        timestamp_after = datetime.datetime.fromtimestamp(1)
        time_filter_str, time_filter_vars = sphinx._make_sql_time_filter(
            created_after=None,
            created_before=timestamp_before,
            updated_after=timestamp_after,
        )
        # updated after creates `(updated_at or pushed_at)` and the "duplicates" var
        assert (
            time_filter_str
            == "and created_at <= %s and pushed_or_updated_at >= %s"
        )
        assert time_filter_vars == [timestamp_before.timestamp(), timestamp_after.timestamp()]

    def test_make_hosting_service_filters_empty(self):
        sphinx = SphinxSearch()
        (
            hosting_service_filters,
            hosting_service_filter_vars,
        ) = sphinx._make_hosting_service_filters([])

        assert hosting_service_filters == ""
        assert hosting_service_filter_vars == []

    def test_make_hosting_service_filters_one(self):
        sphinx = SphinxSearch()
        (
            hosting_service_filters,
            hosting_service_filter_vars,
        ) = sphinx._make_hosting_service_filters([1])

        assert hosting_service_filters == "and hosting_service_id != %s"
        assert hosting_service_filter_vars == [1]

    def test_make_hosting_service_filters_many(self):
        sphinx = SphinxSearch()
        (
            hosting_service_filters,
            hosting_service_filter_vars,
        ) = sphinx._make_hosting_service_filters([1, 2])

        assert (
            hosting_service_filters
            == "and hosting_service_id != %s and hosting_service_id != %s"
        )
        assert hosting_service_filter_vars == [1, 2]
