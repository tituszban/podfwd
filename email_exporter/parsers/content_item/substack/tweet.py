from ..content_item_abc import ContentItemABC
from ssml import tags
from abc import ABC, abstractmethod
from ..util import get_text_content
import re
from ... import description_item


class TweetComponent(ABC):
    def __init__(self, component):
        self.component = component

    @abstractmethod
    def get_text(self):
        return []

    @staticmethod
    @abstractmethod
    def match_component(component):
        raise NotImplementedError()


class NullComponent(TweetComponent):

    def get_text(self):
        return []

    @staticmethod
    def match_component(component):
        return True


class Footer(NullComponent):

    @staticmethod
    def match_component(component):
        try:
            if component.name not in ("div", "a"):
                return False
            if component.name == "a" and len(component.contents) != 1:
                return False

            div = component if component.name == "div" else component.div

            return tuple([c.name for c in div.contents]) in [
                ("p", "span", "span"),
                ("p", "span"),
                ("p",)
            ] and len(div.p.contents) == 1
        except AttributeError:
            return False


class Header(TweetComponent):
    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        try:
            return component.name == "div" and \
                [c.name for c in component.contents] == ["img", "span", "span"]
        except AttributeError:
            return False


class Embed(TweetComponent):

    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        if component.name != "a":
            return False

        if [c.name for c in component.contents] != ["img", "span", "span", "span"]:
            return False

        return True

    @property
    def title(self):
        try:
            return get_text_content(self.component.span)
        except AttributeError:
            return ""


class Link(TweetComponent):

    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        return component.name == "a" and len(component.contents) == 1 and not hasattr(component.contents[0], "contents")


class FakeLink(TweetComponent):

    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        return component.name == "span" and len(component.contents) == 1 and\
            not hasattr(component.contents[0], "contents")


class Text(TweetComponent):

    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        return not hasattr(component, "contents")


class Image(TweetComponent):

    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        def _all_children_are_div_or_img(_component):
            if _component.name == "img":
                return True
            if _component.name == "div":
                return all(map(_all_children_are_div_or_img, _component.contents))
            return False

        return _all_children_are_div_or_img(component)


class RetweetHeader(TweetComponent):
    def get_text(self):
        return super().get_text()

    @staticmethod
    def match_component(component):
        try:
            return component.name == "p" and \
                [c.name for c in component.contents] == ["span", "span"]
        except AttributeError:
            return False


class RegularTweet:
    def __init__(self, header, contents, footer):
        self._header = header
        self._contents = contents
        self._footer = footer

    def _content_to_ssml(self):
        text_content = [item for item in self._contents if isinstance(item, (Text, FakeLink))]

        text = ' '.join([get_text_content(item.component, nl_char=" ") for item in text_content]).strip()

        text = re.sub(r"https://t.co/\w+", "", text)

        if text:
            yield tags.PText(text)

        if len(embeds := [item for item in self._contents if isinstance(item, Embed)]) > 0:
            for embed in embeds:
                if (title := embed.title):
                    yield tags.PText(f"Linking to: {title}.")

    def to_ssml(self):
        return [
            tags.Break(time="500ms"),
            tags.PSText(f"Tweet by {self.username}:"),
            *list(self._content_to_ssml()),
            tags.Break(time="500ms"),
        ]

    @property
    def name(self):
        if not self._header:
            return None
        return self._header.component.find_all("span")[0].text.strip()

    @property
    def username(self):
        if not self._header:
            return None
        return self._header.component.find_all("span")[-1].text.strip()

    @property
    def date(self):
        if not self._footer:
            return None
        return self._footer.component.div.find_all("p")[0].text.strip()

    @property
    def retweet_count(self):
        if not self._footer:
            return None
        spans = self._footer.component.div.find_all("span", recursive=False)
        if len(spans) == 0:
            return 0

        if len(spans) == 2:
            return int(spans[0].span.text.replace(",", ""))

        if "Likes" in spans[0].text:
            return 0
        return int(spans[0].span.text.replace(",", ""))

    @property
    def like_count(self):
        if not self._footer:
            return None
        spans = self._footer.component.div.find_all("span", recursive=False)
        if len(spans) == 0:
            return 0

        if len(spans) == 2:
            return int(spans[1].span.text.replace(",", ""))

        if "Likes" in spans[0].text:
            return int(spans[0].span.text.replace(",", ""))
        return 0


class QuoteTweet(RegularTweet):
    def __init__(self, header, contents, footer, quoted_tweet):
        super().__init__(header, contents, footer)
        self._quoted_tweet = quoted_tweet

    def to_ssml(self):
        return [
            tags.Break(time="500ms"),
            tags.PSText(f"Tweet by {self._quoted_tweet.username}:"),
            *list(self._quoted_tweet._content_to_ssml()),
            tags.PSText(f"To which {self.username} replied:"),
            *list(self._content_to_ssml()),
            tags.Break(time="500ms"),
        ]


class Tweet(ContentItemABC):

    tweet_components = [
        Footer,
        Embed,
        Header,
        Image,
        Link,
        FakeLink,
        Text,
        RetweetHeader,
        NullComponent
    ]

    @staticmethod
    def is_main_body(component):
        if component.name != "a":
            return False

        if len(divs := component.find_all("div", recursive=False)) <= 0:
            return False

        if not Header.match_component(divs[0]):
            return False

        return True

    @staticmethod
    def is_retweet_body(component):
        if component.name != "div":
            return False

        if len(ps := component.find_all("p", recursive=False)) <= 0:
            return False

        if not RetweetHeader.match_component(ps[0]):
            return False

        return True

    @staticmethod
    def decomponse_tweet(component):
        def _match_component(_component):
            for tweet_component in Tweet.tweet_components:
                if tweet_component.match_component(_component):
                    return tweet_component(_component)

        for c in component.contents:
            if Tweet.is_main_body(c):
                for cc in c.contents:
                    if Tweet.is_retweet_body(cc):
                        for ccc in cc.contents:
                            yield _match_component(ccc)
                    else:
                        yield _match_component(cc)
            else:
                yield _match_component(c)

    @staticmethod
    def to_tweet(component):
        tweet_components = list(Tweet.decomponse_tweet(component))

        if len(tweet_components) < 3 or not isinstance(tweet_components[0], Header) or\
                not isinstance(tweet_components[-1], Footer):
            raise RuntimeError("Cannot parse malformed tweet")

        header = tweet_components[0]
        footer = tweet_components[-1]
        tweet_components = tweet_components[1:-1]

        if any([isinstance(tc, RetweetHeader) for tc in tweet_components]):
            i = next(i for i, tc in enumerate(tweet_components) if isinstance(tc, RetweetHeader))
            return QuoteTweet(
                header,
                tweet_components[:i],
                footer,
                RegularTweet(
                    tweet_components[i],
                    tweet_components[i + 1:],
                    None
                )
            )

        return RegularTweet(
            header,
            tweet_components,
            footer
        )

    def get_ssml(self):
        try:
            tweet = Tweet.to_tweet(self._component)
            return tweet.to_ssml()
        except RuntimeError:
            return [
                tags.Break(time="500ms"),
                tags.PSText(f"Broken tweet: Fix me.")
            ]

    def get_description(self):
        return [
            description_item.Embed(self._component)
        ]

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        if "class" in component.attrs and "tweet" in component["class"]:    # Directly received
            return True

        if component.name == "div" and any([
                img["alt"].startswith("Twitter avatar for")
                for img in component.find_all("img")
                if "alt" in img.attrs and img["alt"]]):
            return True

        return False
