from ..generic import NullContentItem


class HorizontalRule(NullContentItem):
    """
    Matches horizontal rule cards in Ghost emails.
    These are table elements with class "kg-hr-card" used as section dividers.
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match table elements with class "kg-hr-card"
        if component.name == "table" and "class" in component.attrs:
            if "kg-hr-card" in component["class"]:
                return True

        return False
