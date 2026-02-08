from ..content_item_abc import ContentItemABC
from .subscribe_button import SubscribeButton
from .captioned_image import CaptionedImage
from .header_logo import HeaderLogo
from .footer import Footer

items: list[type[ContentItemABC]] = [
    SubscribeButton,
    CaptionedImage,
    HeaderLogo,
    Footer,
]
