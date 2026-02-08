from ..generic import NullContentItem


class SubscribeButton(NullContentItem):
    """
    Matches subscribe/upgrade buttons in mailgun emails.
    These are typically tables with class "button" containing a call-to-action.
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match table elements with class "button"
        if component.name == "table" and "class" in component.attrs:
            if "button" in component["class"]:
                return True

        # Match the subscribe button inner td
        if component.name == "td" and "class" in component.attrs:
            if "subscribe-button-inner" in component["class"]:
                return True

        return False
