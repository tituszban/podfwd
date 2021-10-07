from .null_tc_table import NullTcTable
from .tc_table_abc import TcTableABC


class SocialTcTable(NullTcTable):
    @staticmethod
    def match_component(component):
        try:
            if not TcTableABC._has_n_child_of_type(component, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr, "td"):
                return False

            imgs = component.tr.td.find_all("img")
            if len(imgs) <= 3:
                return False

            return True
        except AttributeError:
            return False
