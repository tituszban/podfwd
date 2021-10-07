from .tc_table_abc import TcTableABC
from ...content_item import ContentItem


class ContentTcTable(TcTableABC):
    def get_items(self):
        for component in self._component.tr.td.table.tr.td.table.tr.td.contents:
            if component == "\n":
                continue
            yield ContentItem.to_item(component)

    @staticmethod
    def match_component(component):
        try:
            if not TcTableABC._has_n_child_of_type(component, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr, "td"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td, "table"):
                return False

            if not TcTableABC._has_n_child_of_type(component.tr.td.table, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td.table.tr, "td"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td.table.tr.td, "table"):
                return False

            if not TcTableABC._has_n_child_of_type(component.tr.td.table.tr.td.table, "tr"):
                return False
            if not TcTableABC._has_n_child_of_type(component.tr.td.table.tr.td.table.tr, "td"):
                return False

            return True

        except AttributeError:
            return False
