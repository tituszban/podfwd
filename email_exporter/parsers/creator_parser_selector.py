from .parser_selector import ParserSelector


class CreatorParserSelector(ParserSelector):
    def get_parser(self, content_item):
        return self._get_parser(content_item.owner)
