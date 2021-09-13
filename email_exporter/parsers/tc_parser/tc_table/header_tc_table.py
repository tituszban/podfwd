from .tc_table_abc import TcTableABC
from ...content_item import ContentItem

class HeaderTcTable(TcTableABC):
    def get_items(self):
        return [
            ContentItem.Special.to_tc_header(self._component, self._content_item)
        ]

    @staticmethod
    def match_component(component):
        title_separator = "•"

        try:
            trs = component.find_all("tr", recursive=False)
            if len(trs) != 3:
                return False
            if title_separator not in trs[2].td.p.text:
                return False
            return True
        except AttributeError:
            return False
