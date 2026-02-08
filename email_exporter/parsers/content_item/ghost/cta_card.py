from ..generic import NullContentItem


class CtaCard(NullContentItem):
    """
    Matches CTA (Call to Action) card elements in Ghost emails.
    These are promotional cards with upgrade/subscribe buttons.
    Typically table elements with class "kg-cta-card".
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match table elements with class "kg-cta-card"
        if component.name == "table" and "class" in component.attrs:
            if "kg-cta-card" in component["class"]:
                return True

        return False
