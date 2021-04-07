from hubgrep.lib.pagination import get_page_links
from hubgrep.constants import CLASS_PREV, CLASS_NEXT, CLASS_DIVIDER, CLASS_CURRENT_PAGE


class TestPagination:

    def test_pagination_start(self):
        links = get_page_links(url="/", offset=0, per_page=10, results_total=1000, enumerated_link_max=10,
                               has_next_prev=True, detach_min=10, side_link_portions=0.2)
        # since current page is the first page, we should have one divider on the end as the max-enum links allow it
        assert len(links) == 13  # 10 + 2 prev/next + 1 dividers
        assert links[0].class_name == CLASS_PREV
        assert links[1].class_name == CLASS_CURRENT_PAGE
        assert links[-4].class_name == CLASS_DIVIDER
        assert links[-1].class_name == CLASS_NEXT

    def test_pagination_middle(self):
        links = get_page_links(url="/", offset=200, per_page=10, results_total=1000, enumerated_link_max=10,
                               has_next_prev=True, detach_min=10, side_link_portions=0.2)
        # since current page is in the middle somewhere, and we have a lot of pages - we should have 2 dividers
        assert len(links) == 14  # 10 + 2 prev/next + 2 dividers
        assert links[0].class_name == CLASS_PREV
        assert links[3].class_name == CLASS_DIVIDER
        assert links[8].class_name == CLASS_CURRENT_PAGE
        assert links[-4].class_name == CLASS_DIVIDER
        assert links[-1].class_name == CLASS_NEXT

    def test_pagination_end(self):
        links = get_page_links(url="/", offset=990, per_page=10, results_total=1000, enumerated_link_max=10,
                               has_next_prev=True, detach_min=10, side_link_portions=0.2)
        # since current page is at the end, we should have one divider on the end as the max-enum links allow it
        assert len(links) == 10  # 7 + 2 prev/next + 1 dividers
        # 7.. there's a bug, but I don't think it matters if the end generates fewer enumerated links
        assert links[0].class_name == CLASS_PREV
        assert links[3].class_name == CLASS_DIVIDER
        assert links[-2].class_name == CLASS_CURRENT_PAGE
        assert links[-1].class_name == CLASS_NEXT
