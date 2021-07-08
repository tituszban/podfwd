from functools import reduce
import re


class TweetItem:
    def __init__(self, component):
        spans = [s.get_text() for s in component.find_all("span")]
        author_candidates = [s for s in spans if s.startswith("@")]
        author = author_candidates[0] if len(
            author_candidates) > 0 else "Unknown"
        span_text = [s for s in spans if not re.match(r"^\d+$", s)]

        tweet = reduce(
            lambda txt, s: txt.replace(s, ""),
            span_text,
            component.get_text()
        )

        self.component = component
        self.name = "tweet"
        self.text = f"Tweet by {author}: " + tweet
        self.is_only_link = False
        self.links = []
