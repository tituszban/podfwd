from .null_tc_table import NullTcTable
from .content_tc_table import ContentTcTable


class SponsoredTcTable(NullTcTable):
    @staticmethod
    def match_component(component):
        if not ContentTcTable.match_component(component):
            return

        try:
            h3s = component.tr.td.table.tr.td.table.tr.td.find_all("h3")
            if len(h3s) <= 0:
                return False

            if not any("Sponsored by" in h3.text for h3 in h3s):
                return False

            return True

        except AttributeError:
            return False
