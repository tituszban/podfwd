from .tc_table_abc import TcTableABC


class NullTcTable(TcTableABC):
    def get_items(self):
        return []

    @staticmethod
    def match_component(component):
        return True
