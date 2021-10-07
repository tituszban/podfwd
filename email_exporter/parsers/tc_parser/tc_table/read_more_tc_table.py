from .null_tc_table import NullTcTable
from .tc_table_abc import TcTableABC


class ReadMoreTcTable(NullTcTable):
    @staticmethod
    def match_component(component):
        try:
            if not TcTableABC._has_n_child_of_type(component, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr, "td"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td, "p"):
                return False

            if not component.tr.td.p.text.strip().startswith("Read more"):
                return False

            return True

        except AttributeError:
            return False
