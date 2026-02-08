from ..generic import NullContentItem


class ButtonCard(NullContentItem):
    """
    Matches button card tables in Ghost emails.
    These are table elements with class "kg-button-card" containing
    call-to-action buttons.
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match table elements with class "kg-button-card"
        if component.name == "table" and "class" in component.attrs:
            if "kg-button-card" in component["class"]:
                return True

        return False
