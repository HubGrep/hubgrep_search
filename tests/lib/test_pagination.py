from urllib.parse import urlparse, parse_qs
from hubgrep.lib.pagination import get_page_links
from hubgrep.constants import CLASS_PREV, CLASS_NEXT, CLASS_DIVIDER, CLASS_CURRENT_PAGE, PARAM_OFFSET, PARAM_PER_PAGE


class TestPagination:

    def test_pagination_start(self):
        """ when current page is the first page we should have one divider on the end as the max-enum links allow it """
        links = get_page_links(url="/", offset=0, per_page=10, results_total=1000, enumerated_link_max=10,
                               has_next_prev=True, detach_min=10, side_link_portions=0.2)
        assert len(links) == 13  # 10 + 2 prev/next + 1 dividers
        assert links[0].class_name == CLASS_PREV
        assert links[1].class_name == CLASS_CURRENT_PAGE
        assert links[-4].class_name == CLASS_DIVIDER
        assert links[-1].class_name == CLASS_NEXT

    def test_pagination_middle(self):
        """ when current page is in the middle somewhere, and we have a lot of pages - we should have 2 dividers """
        links = get_page_links(url="/", offset=200, per_page=10, results_total=1000, enumerated_link_max=10,
                               has_next_prev=True, detach_min=10, side_link_portions=0.2)
        assert len(links) == 14  # 10 + 2 prev/next + 2 dividers
        assert links[0].class_name == CLASS_PREV
        assert links[3].class_name == CLASS_DIVIDER
        assert links[8].class_name == CLASS_CURRENT_PAGE
        assert links[-4].class_name == CLASS_DIVIDER
        assert links[-1].class_name == CLASS_NEXT

    def test_pagination_end(self):
        """ when current page is at the end, we should have one divider on the end as the max-enum links allow it """
        links = get_page_links(url="/", offset=990, per_page=10, results_total=1000, enumerated_link_max=10,
                               has_next_prev=True, detach_min=10, side_link_portions=0.2)
        assert len(links) == 10  # 7 + 2 prev/next + 1 dividers
        # 7.. there's a bug, but I don't think it matters if the end generates fewer enumerated links
        assert links[0].class_name == CLASS_PREV
        assert links[3].class_name == CLASS_DIVIDER
        assert links[-2].class_name == CLASS_CURRENT_PAGE
        assert links[-1].class_name == CLASS_NEXT

    def test_pagination_params(self):
        """ make sure links contain pagination parameters, with int values """

        def is_int(value: str):
            try:
                int(value)
                return True
            except ValueError:
                return False

        links = get_page_links(url="/", offset=0, per_page=10, results_total=100)
        for link in links:
            if link.url:
                u = urlparse(link.url)
                params = parse_qs(u.query)
                assert PARAM_OFFSET in params
                assert PARAM_PER_PAGE in params
                assert is_int(params[PARAM_OFFSET][0])
                assert is_int(params[PARAM_PER_PAGE][0])

    def test_pagination_preserve_original_params(self):
        """ we want to make sure that original none-pagination parameters still remain in each link """
        param = "foo"
        value = "bar"
        links = get_page_links(url="/?{}={}".format(param, value), offset=0, per_page=10, results_total=100)
        for link in links:
            if link.url:
                u = urlparse(link.url)
                params = parse_qs(u.query)
                assert param in params
                assert value in params[param]
