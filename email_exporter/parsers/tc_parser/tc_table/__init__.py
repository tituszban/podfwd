from .tc_table_abc import TcTableABC
from .content_tc_table import ContentTcTable
from .content_with_image_tc_table import ContentWithImageTcTable
from .footer_tc_table import FooterTcTable
from .header_tc_table import HeaderTcTable
from .jobs_tc_table import JobsTcTable
from .null_tc_table import NullTcTable
from .read_more_tc_table import ReadMoreTcTable
from .social_tc_table import SocialTcTable
from .sponsored_tc_table import SponsoredTcTable


class TcTable:

    tc_tables: list[type[TcTableABC]] = [
        HeaderTcTable,
        SponsoredTcTable,
        JobsTcTable,
        ReadMoreTcTable,
        SocialTcTable,
        FooterTcTable,
        ContentTcTable,
        ContentWithImageTcTable,
        NullTcTable
    ]

    @staticmethod
    def get_table(component, content_item) -> TcTableABC:
        for tc_table in TcTable.tc_tables:
            if tc_table.match_component(component):
                return tc_table(component, content_item)
        raise Exception("No component were matched")
