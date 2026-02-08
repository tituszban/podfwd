from ..generic import NullContentItem


class FeedbackButtons(NullContentItem):
    """
    Matches feedback buttons container in Ghost emails.
    These are table elements with class "feedback-buttons" that contain
    comment/share/like buttons.
    """

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match table elements with class "feedback-buttons"
        if component.name == "table" and "class" in component.attrs:
            if "feedback-buttons" in component["class"]:
                return True

        return False
