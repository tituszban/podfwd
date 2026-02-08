from ..generic import NullContentItem


class Paywall(NullContentItem):
    """
    Matches paywall sections in Ghost emails.
    These are div elements with class "kg-paywall" that show upgrade prompts.
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match div elements with class "kg-paywall"
        if component.name == "div" and "class" in component.attrs:
            if "kg-paywall" in component["class"]:
                return True

        return False
