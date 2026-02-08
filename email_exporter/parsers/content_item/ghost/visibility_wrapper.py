from ..generic import NullContentItem


class VisibilityWrapper(NullContentItem):
    """
    Matches visibility wrapper divs in Ghost emails.
    These are div elements with class "kg-visibility-wrapper" that typically
    contain CTA cards or other promotional content. We filter these out since
    they usually wrap promotional content.
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match div elements with class "kg-visibility-wrapper"
        if component.name == "div" and "class" in component.attrs:
            if "kg-visibility-wrapper" in component["class"]:
                return True

        return False
