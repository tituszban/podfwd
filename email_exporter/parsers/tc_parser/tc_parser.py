from email_exporter.inbox.inbox_item import InboxItem
from ..item_emitter import ItemEmitter
from .tc_table import TcTable


class TcItemEmitter(ItemEmitter):
    def get_items(self, inbox_item: InboxItem):
        trs = inbox_item.soup.table.find_all("tr", recursive=False)

        tables = [TcTable.get_table(tr.td.table, inbox_item) for tr in trs]

        for table in tables:
            for item in table.get_items():
                yield item
