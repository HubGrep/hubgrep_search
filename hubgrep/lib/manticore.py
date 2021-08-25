"""
Manticore interface and result-class for Manticore.
"""

import logging
import datetime


from typing import List, Dict

from flask import current_app
import pymysql.cursors
from pymysql.cursors import DictCursor
from pymysql.err import ProgrammingError
from collections import OrderedDict
from urllib.parse import urljoin

from hubgrep.models import Repository

logger = logging.getLogger(__name__)


class UserError(Exception):
    pass


class SearchResult:
    def __init__(self, repo: Repository, weight: float):
        self.hosting_service_type = repo.hosting_service.type
        self.name = repo.name
        self.username = repo.username
        self.description = repo.description
        self.created_at = repo.created_at
        self.updated_at = repo.updated_at
        self.pushed_at = repo.pushed_at
        self.stars_count = repo.stars_count
        self.forks_count = repo.forks_count

        self.is_fork = repo.is_fork
        self.is_archived = repo.is_archived
        self.is_mirror = repo.is_mirror
        self.is_empty = repo.is_empty
        self.homepage_url = repo.homepage_url
        self.repo_url = repo.repo_url
        self.weight = weight

        self.age = datetime.datetime.now() - repo.created_at
        self.weighted_score = None
        #self.set_weighted_score()

    def set_weighted_score(self):
        scores = []
        scoring_functions = [
            self.get_recent_activity_score,
            self.get_active_time_score,
            self.get_description_score,
            self.get_is_archived_score
        ]
        for f in scoring_functions:
            scores.append(f())
        logger.info(scoring_functions)
        logger.info(scores)
        score = sum(scores) / len(scores)
        logger.info(score)
        self.weight = self.weight * score

    def get_description_score(self):
        if self.description:
            words = self.description.split()
            if len(words) < 6:
                return len(words) * 0.1
            return 1
        else:
            return 0

    def get_is_archived_score(self):
        if self.is_archived:
            return 0.3
        return 1

    def get_active_time_score(self):
        last_update = self.pushed_at or self.updated_at
        days_between_first_last_pushed = (last_update - self.created_at).days

        weeks_between_first_last_pushed = int(days_between_first_last_pushed / 7)
        months_between_first_and_last_push = int(weeks_between_first_last_pushed / 4)
        if months_between_first_and_last_push > 6:
            return 1
        score = 1 - (6 - months_between_first_and_last_push) * 0.1
        return score

    def get_recent_activity_score(self):
        if self.pushed_at and self.updated_at:
            time_since_last_push = datetime.datetime.now() - max(
                self.pushed_at, self.updated_at
            )
        elif self.pushed_at:
            time_since_last_push = datetime.datetime.now() - self.pushed_at
        elif self.updated_at:
            time_since_last_push = datetime.datetime.now() - self.updated_at
        else:
            return 0.5

        days_since_last_push = time_since_last_push.days
        weeks_since_last_push = int(days_since_last_push / 7)
        months_since_last_push = int(weeks_since_last_push / 4)

        if months_since_last_push < 6:
            return 1

        weighted_score = max(0, 1 - (months_since_last_push * 0.1))
        logger.info(weighted_score)
        return weighted_score

    def __repr__(self):
        return f"<{self.username}/{self.name} ({self.weight})>"


class SearchMeta:
    def __init__(self, meta_rows):
        """
        meta_rows comes from "show meta" after a query and should look like:
        [
            {
                "Variable_name": "warning",
                "Value": "index repos: Fields specified in field_weights option not found: [repo_name]",
            },
            {"Variable_name": "total", "Value": "1000"},
            {"Variable_name": "total_found", "Value": "3847"},
            {"Variable_name": "time", "Value": "0.009"},
            {"Variable_name": "keyword[0]", "Value": "test"},
            {"Variable_name": "docs[0]", "Value": "3847"},
            {"Variable_name": "hits[0]", "Value": "4738"},
        ]
        """
        meta_dict = dict()
        for row in meta_rows:
            key = row["Variable_name"]
            value = row["Value"]
            meta_dict[key] = value

        # count of actual returned ids (limited to 1000)
        self.total = int(meta_dict.get("total", 0))
        # count of theoretical results (unlimited)
        self.total_found = int(meta_dict.get("total_found", 0))
        # time search in manticore took
        self.time = float(meta_dict.get("time", 0))
        self.warning = meta_dict.get("warning", None)


class ManticoreSearch:
    """Interface for searching via Manticore."""

    name = "Manticore"

    @classmethod
    def _make_sql_time_filter(
        cls,
        created_after: datetime.datetime,
        created_before: datetime.datetime,
        updated_after: datetime.datetime,
        pushed_after: datetime.datetime,
    ):
        """
        returns the time filters as a string, as well as a list of vars to use in the mysql query

        (we dont include the vars here so that the mysql lib can do the needed string escaping and converting)
        """
        time_filters = []
        time_filter_vars = []
        if created_after:
            time_filters.append("created_at >= %s")
            time_filter_vars.append(int(created_after.timestamp()))
        if created_before:
            time_filters.append("created_at <= %s")
            time_filter_vars.append(int(created_before.timestamp()))
        if updated_after:
            time_filters.append("updated_at >= %s")
            time_filter_vars.append(int(updated_after.timestamp()))
        if pushed_after:
            time_filters.append("pushed_at >= %s")
            time_filter_vars.append(int(pushed_after.timestamp()))
        if time_filters:
            # construct "and a and b and c"
            time_filters_str = " and ".join(time_filters)
            time_filters_str = "and " + time_filters_str
        else:
            time_filters_str = ""
        return time_filters_str, time_filter_vars

    @classmethod
    def _make_bool_filters(
        cls,
        exclude_forks: bool,
        exclude_archived: bool,
        exclude_mirror: bool,
        exclude_empty: bool,
    ):
        # if False in (exclude_forks, exclude_archived, exclude_empty, exclude_mirror):
        filters = []
        if exclude_forks:
            filters.append("is_fork = 0")
        if exclude_archived:
            filters.append("is_archived = 0")
        if exclude_mirror:
            filters.append("is_mirror = 0")
        if exclude_empty:
            filters.append("is_empty = 0")

        if filters:
            # "and is_fork=true and .. and .."
            return "and " + " and ".join(filters)
        return ""

    @classmethod
    def _make_hosting_service_filters(cls, exclude_hosting_service_ids: List[int]):
        hosting_service_filters = []
        hosting_service_filter_vars = []
        for hosting_service_id in exclude_hosting_service_ids:
            hosting_service_filters.append("hosting_service_id != %s")
            hosting_service_filter_vars.append(hosting_service_id)

        if hosting_service_filters:
            # we start with "and ..."
            hosting_service_filters_str = "and " + " and ".join(hosting_service_filters)
        else:
            hosting_service_filters_str = ""
        return hosting_service_filters_str, hosting_service_filter_vars

    @classmethod
    def _search_manticore(
        cls,
        search_phrase: str,
        exclude_hosting_service_ids: List[int],
        exclude_forks: bool = None,
        exclude_archived: bool = None,
        exclude_mirror: bool = None,
        exclude_empty: bool = None,
        created_after: datetime.datetime = None,
        created_before: datetime.datetime = None,
        updated_after: datetime.datetime = None,
        pushed_after: datetime.datetime = None,
    ) -> (Dict[int, Dict], SearchMeta):
        connection = pymysql.connect(
            host=current_app.config["MANTICORE_HOST"],
            port=9306,
            cursorclass=pymysql.cursors.DictCursor,
        )

        time_filters, time_filter_vars = cls._make_sql_time_filter(
            created_after, created_before, updated_after, pushed_after
        )
        bool_filters = cls._make_bool_filters(
            exclude_forks,
            exclude_archived,
            exclude_mirror,
            exclude_empty,
        )

        (
            hosting_service_filters,
            hosting_service_filter_vars,
        ) = cls._make_hosting_service_filters(
            exclude_hosting_service_ids=exclude_hosting_service_ids
        )

        with connection:
            with connection.cursor() as cursor:
                sql_template = f"""
                    select id, weight(), (weight() * {score}) as weighted_score
                    from repos
                    where
                        match(%s)
                    {time_filters} {bool_filters} {hosting_service_filters}
                    limit 1000
                    option
                        ranker=sph04,
                        field_weights=(name=60, description=10)
                    """
                query = cursor.mogrify(
                    sql_template,
                    (search_phrase, *time_filter_vars, *hosting_service_filter_vars),
                )
                logger.info(query)
                cursor.execute(query)
                result_dicts = cursor.fetchall()

                sql_query_stats = "show meta"
                cursor.execute(sql_query_stats)
                meta_rows = cursor.fetchall()
                meta = SearchMeta(meta_rows)

        # ordereddicts keep the order in which the items are added
        # (and our results should be ordered)
        search_results_by_id = OrderedDict()
        for result_dict in result_dicts:
            search_results_by_id[result_dict["id"]] = {
                "weight": result_dict["weighted_score"]
            }
        return search_results_by_id, meta

    @classmethod
    def _get_from_db(cls, ids: List[int]) -> List[Repository]:
        repos = Repository.query.filter(Repository.id.in_(ids)).all()
        return repos

    @classmethod
    def search(
        cls,
        search_phrase: str,
        results_offset: int,
        results_per_page: int,
        exclude_hosting_service_ids: List[int],
        exclude_forks: bool,
        exclude_archived: bool,
        exclude_mirror: bool,
        exclude_empty: bool,
        created_after: datetime.datetime = None,
        created_before: datetime.datetime = None,
        updated_after: datetime.datetime = None,
        pushed_after: datetime.datetime = None,
    ) -> List[SearchResult]:
        try:
            results, meta = cls._search_manticore(
                search_phrase,
                exclude_hosting_service_ids=exclude_hosting_service_ids,
                exclude_forks=exclude_forks,
                exclude_archived=exclude_archived,
                exclude_mirror=exclude_mirror,
                exclude_empty=exclude_empty,
                created_after=created_after,
                created_before=created_before,
                updated_after=updated_after,
                pushed_after=pushed_after,
            )
        except ProgrammingError as e:
            if len(e.args) == 2:
                # (1064, index 'repos': query error: no field 'repo_name' found in schema)
                if e.args[0] == 1064:
                    raise UserError(e.args[1])
            raise UserError("unknown error")

        # get only the keys for the requested page
        from_idx = results_offset
        to_idx = results_offset + results_per_page
        results_page_keys = list(results.keys())[from_idx:to_idx]
        db_results = cls._get_from_db(results_page_keys)

        # transform to "SearchResult" for frontend, adding result weights
        search_results = []
        for result in db_results:
            weight = results[result.id]["weight"]
            search_result = SearchResult(result, weight)
            search_results.append(search_result)

        search_results = sorted(
            search_results,
            key=lambda r: (r.weight, r.age),
            reverse=True,
        )
        return search_results, meta

    @staticmethod
    def default_api_url_from_landingpage_url(landingpage_url: str) -> str:
        return urljoin(landingpage_url, "/api/v1/")
