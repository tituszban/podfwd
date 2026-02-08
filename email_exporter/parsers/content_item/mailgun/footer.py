from ..generic import NullContentItem


class Footer(NullContentItem):
    """
    Matches footer section in mailgun emails.
    These are typically td elements with class "footer".
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match td elements with class "footer"
        if component.name == "td" and "class" in component.attrs:
            if "footer" in component["class"]:
                return True

        return False
