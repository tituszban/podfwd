from ..generic import NullContentItem


class HeaderLogo(NullContentItem):
    """
    Matches header logo section in mailgun emails.
    These are typically td elements with class "header-logo".
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match td elements with class "header-logo"
        if component.name == "td" and "class" in component.attrs:
            if "header-logo" in component["class"]:
                return True

        return False
