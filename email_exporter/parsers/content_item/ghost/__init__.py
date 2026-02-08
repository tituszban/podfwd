from ..content_item_abc import ContentItemABC
from .cta_card import CtaCard
from .paywall import Paywall
from .feedback_buttons import FeedbackButtons
from .footer import Footer
from .footer_powered import FooterPowered
from .horizontal_rule import HorizontalRule
from .visibility_wrapper import VisibilityWrapper
from .button_card import ButtonCard
from .image_card import ImageCard

items: list[type[ContentItemABC]] = [
    CtaCard,
    Paywall,
    FeedbackButtons,
    Footer,
    FooterPowered,
    HorizontalRule,
    VisibilityWrapper,
    ButtonCard,
    ImageCard,
]
