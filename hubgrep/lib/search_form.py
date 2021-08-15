"""
Value-object for HubGreps main search form.

Note: Not the actual HTML form, which can be found in -
'hubgrep/frontend_blueprint/templates/components/search_form/search_form.html'
"""
import pytz
from typing import List, Dict
from collections import namedtuple
from datetime import datetime
from flask import request
from hubgrep.models.hosting_service import HostingService
from hubgrep.constants import DATE_FORMAT

Checkbox = namedtuple("checkbox", "service_id id label is_checked")
utc = pytz.UTC


class SearchForm:
    """Input-fields relate to either a repository property or a hosting-service where they a found."""

    search_phrase: str
    exclude_service_checkboxes: Dict[int, Checkbox]
    exclude_forks: bool
    exclude_archived: bool
    exclude_disabled: bool
    exclude_mirror: bool
    created_after: str
    created_before: str
    updated_after: str
    pushed_after: str
    created_after_dt: datetime
    created_before_dt: datetime
    updated_after_dt: datetime
    pushed_after_dt: datetime

    def __init__(
        self,
        search_phrase: str = None,
        exclude_service_checkboxes: Dict[int, Checkbox] = None,
        exclude_forks: bool = False,
        exclude_archived: bool = False,
        exclude_disabled: bool = False,
        exclude_mirror: bool = False,
        created_after: str = None,
        created_before: str = None,
        updated_after: str = None,
        pushed_after: str = None,
        created_after_dt: datetime = None,
        created_before_dt: datetime = None,
        updated_after_dt: datetime = None,
        pushed_after_dt: datetime = None,
    ):
        """
        :param search_phrase: free text used for searching
        :param exclude_service_checkboxes: a list of "Checkbox" tuples
        :param exclude_forks: bool - removes forks form results
        :param exclude_archived: bool - removes archived repositories from results
        :param created_after: string - results have to be created after this date
        :param created_before: string - results have to be created before this date
        :param updated_after: string - only include results that have been updated after this date
        :param created_after_dt: datetime for created_after (resolved from created_after when omitted)
        :param created_before_dt: datetime for created_before (resolved from created_before when omitted)
        :param updated_after_dt: datetime for updated_after (resolved from updated_after when omitted)
        :param pushed_after_dt: datetime for pushed_after (resolved from pushed_after when omitted)
        """
        self.search_phrase = search_phrase
        self.exclude_service_checkboxes = exclude_service_checkboxes
        self.exclude_forks = exclude_forks
        self.exclude_archived = exclude_archived
        self.exclude_disabled = exclude_disabled
        self.exclude_mirror = exclude_mirror
        self.created_after = created_after
        self.created_before = created_before
        self.updated_after = updated_after
        self.pushed_after = pushed_after
        self.created_after_dt = created_after_dt
        self.created_before_dt = created_before_dt
        self.updated_after_dt = updated_after_dt
        self.pushed_after_dt = pushed_after_dt
        if not created_after_dt and self.created_after:
            self.created_after_dt = SearchForm.get_form_datetime_in_utc(
                self.created_after
            )
        if not created_before_dt and self.created_before:
            self.created_before_dt = SearchForm.get_form_datetime_in_utc(
                self.created_before
            )
        if not updated_after_dt and self.updated_after:
            self.updated_after_dt = SearchForm.get_form_datetime_in_utc(
                self.updated_after
            )
        if not pushed_after_dt and self.pushed_after:
            self.pushed_after_dt = SearchForm.get_form_datetime_in_utc(
                self.pushed_after
            )

    def get_excluded_hosting_service_ids(self):
        excluded_ids = []
        for _, hosting_service_checkbox in self.exclude_service_checkboxes.items():
            if hosting_service_checkbox.is_checked:
                excluded_ids.append(hosting_service_checkbox.service_id)
        return excluded_ids

    @staticmethod
    def get_request_service_checkboxes() -> {}:
        """Create a checkbox for each hosting-service registered on the current HubGrep instance."""
        exclude_service_checkboxes = dict()
        for service in HostingService.query.order_by(HostingService.repo_count.desc()).all():
            is_checked = request.args.get("xs{}".format(service.id), False) == "on"
            exclude_service_checkboxes[service.id] = Checkbox(
                service_id=service.id,
                id="xs{}".format(service.id),
                label=service.domain,
                is_checked=is_checked,
            )
        return exclude_service_checkboxes

    @staticmethod
    def get_form_datetime_in_utc(date: str, date_format: str = DATE_FORMAT):
        """
        Normalize dates into UTC.

        :param date: string - date
        :param date_format: string - parsing format, such as "%Y-%m-%d"
        """
        return utc.localize(datetime.strptime(date, date_format))
