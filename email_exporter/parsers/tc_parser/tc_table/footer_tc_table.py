from .null_tc_table import NullTcTable
from .tc_table_abc import TcTableABC


class FooterTcTable(NullTcTable):
    @staticmethod
    def match_component(component):
        try:
            if not TcTableABC._has_n_child_of_type(component, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr, "td"):
                return False

            ps = component.tr.td.find_all("p")
            if len(ps) != 3:
                return False

            if "Privacy Policy" not in ps[1].text:
                return False

            return True
        except AttributeError:
            return False
