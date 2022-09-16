from ..content_item_abc import ContentItemABC
from .paragraph import Paragraph
from .null_content_item import NullContentItem
from .header import Header
from .list_element import List
from .blockquote import Blockquote
from .empty_paragraph import EmptyParagraph

items: list[type[ContentItemABC]] = [
    Blockquote,
    List,
    Header,
    EmptyParagraph,
    Paragraph,
    NullContentItem
]
