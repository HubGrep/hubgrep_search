""" Create pagination objects (PageLink) used in templating. """
import math
from typing import List
from collections import namedtuple
from urllib.parse import urlparse, parse_qs, ParseResult, urlencode
from flask_babel import gettext
from hubgrep.constants import PARAM_OFFSET, PARAM_PER_PAGE, CLASS_CURRENT_PAGE, CLASS_NEXT, CLASS_PREV, CLASS_DIVIDER

PageLink = namedtuple("PageLink", "url label class_name")
divider_link = PageLink("", "..", CLASS_DIVIDER)


def _get_page_link(u: ParseResult, params: dict, offset: int, per_page: int, label: str,
                   class_name: str = "") -> PageLink:
    """ Construct a PageLink (namedtuple) for use in templating.

    :param u: parsed "urllib" tuple which pagination params will be modified on
    :param params: parsed query parameters from "u"
    :param offset: starting offset for the new page in terms of items shown
    :param per_page: amount of items to display on the new page
    :param label: display label for the PageLink
    :param class_name: optional css class
    """
    params[PARAM_OFFSET] = [str(offset)]
    params[PARAM_PER_PAGE] = [str(per_page)]
    res = ParseResult(scheme=u.scheme, netloc=u.hostname, path=u.path, params=u.params,
                      query=urlencode(params, doseq=True), fragment=u.fragment)
    return PageLink(url=res.geturl(), label=label, class_name=class_name)


def get_page_links(url: str, offset: int, per_page: int, results_total: int, enumerated_link_max: int = 10,
                   has_next_prev: bool = True, detach_min: int = 10, side_link_portions: float = 0.2) -> List[PageLink]:
    """ Constructs a list of PageLinks (namedtuple) for use in templating.

    This list (when able & enabled) will contain a "previous" link at first index and a "next" link as the last item.
    It may also contain empty links as dividers when there are more pages total than shown.

    The constructed list will look like below (".." = divider links):
    [<previous>, <detach_left enum links>, .., <mid_start -enum links- mid_end>, .., <detach_right enum links>, <next>]

    Detached links on left and right will only exist when the ends of the list are further away than what the
    enumerated links in the middle can show (enumerated_link_max). Like so, if current page is nr 12:
    1 2 .. 10 11 12 13 14 15 .. 59 60

    :param url: current url to modify and/or add query params on regarding pagination
    :param offset: starting offset for the new url in terms of items shown
    :param per_page: amount of results shown on the new page
    :param results_total: total maximum for pagination to work within
    :param enumerated_link_max: upper cap for amount of enumerated page-links (but not a cap for the returned list when "has_next_prev" is enabled)
    :param detach_min: no link dividers for total links under this value
    :param has_next_prev: sets label & url for links to adjacent pages (not counted toward link_max), if False it will still include empty PageLinks!
    :param side_link_portions: decimal between 0 - 0.5 assigned to each static end of pagination link-sections
    """
    u = urlparse(url)
    params = parse_qs(u.query)

    links = []
    page_current = offset // per_page
    page_total = math.ceil(results_total / per_page)
    link_total = page_total if page_total < enumerated_link_max else enumerated_link_max
    allow_detach = detach_min <= page_total

    # --- append "previous" link
    if has_next_prev and page_current > 0:
        links.append(_get_page_link(u, params, offset - per_page, per_page, gettext("Previous"), CLASS_PREV))
    else:
        links.append(PageLink("", "", CLASS_PREV))

    # --- append & calculate enumerated links
    side_cnt = math.ceil(link_total * side_link_portions)
    mid_max = link_total - side_cnt * 2
    mid_side_cnt = mid_max // 2
    mid_shift = max(0, page_current + mid_side_cnt - page_total + 2)  # shift mid start/end to avoid links outside total
    mid_start = page_current - mid_side_cnt - mid_shift
    mid_end = page_current + mid_side_cnt - mid_shift

    is_left_detached, is_right_detached = False, False
    if allow_detach:
        if mid_start > side_cnt:
            is_left_detached = True
        if mid_end < page_total - side_cnt:
            is_right_detached = True

    link_indexes_right = list(range(page_total - side_cnt, page_total))
    link_indexes_right.reverse()
    for link_index in range(link_total):
        class_name = ""
        page_number = link_index

        if is_left_detached:
            if link_index >= side_cnt:
                page_number = mid_start + link_index - side_cnt

            if link_index == side_cnt:
                links.append(divider_link)

        if is_right_detached:
            if link_index >= link_total - side_cnt:
                page_number = link_indexes_right.pop()

            if link_index == link_total - side_cnt:
                links.append(divider_link)

        if page_number == page_current:
            class_name = CLASS_CURRENT_PAGE

        links.append(_get_page_link(u, params, page_number * per_page, per_page,
                                    label=str(page_number + 1), class_name=class_name))

    # --- append "next" link
    if has_next_prev and page_current + 1 != page_total and page_total > 1:
        links.append(_get_page_link(u, params, offset + per_page, per_page, gettext("Next"), CLASS_NEXT))
    else:
        links.append(PageLink("", "", CLASS_NEXT))

    return links
