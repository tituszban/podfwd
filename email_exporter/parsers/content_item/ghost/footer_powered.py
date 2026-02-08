from ..generic import NullContentItem


class FooterPowered(NullContentItem):
    """
    Matches "Powered by Ghost" footer section in Ghost emails.
    These are td elements with class "footer-powered".
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match td elements with class "footer-powered"
        if component.name == "td" and "class" in component.attrs:
            if "footer-powered" in component["class"]:
                return True

        return False
