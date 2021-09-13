from .null_tc_table import NullTcTable
from .tc_table_abc import TcTableABC


class JobsTcTable(NullTcTable):
    @staticmethod
    def match_component(component):
        try:
            if not TcTableABC._has_n_child_of_type(component, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr, "td"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td, "table"):
                return False

            if not TcTableABC._has_n_child_of_type(component.tr.td.table, "tr", 2):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td.table.tr, "td"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td.table.tr.td, "h2"):
                return False

            if not component.tr.td.table.tr.td.h2.text.strip().startswith("Newest Jobs"):
                return False

            return True

        except AttributeError:
            return False
