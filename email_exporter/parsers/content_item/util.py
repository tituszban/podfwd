from functools import reduce
import re


def get_text_content(component):
    return reduce(
        lambda txt, c: txt.replace(*c),
        [
            ("\n", ""), ("\r", ""),
            ("—", "-"), ("\xa0", " "), ("–", "-"),
            ("”", '"'), ("“", '"'),
            ("‘", "'"), ("’", "'"),
            ("…", "...")
        ],
        component.get_text(" ", strip=True)).strip()


def is_only_link(component):
    links = component.find_all("a")
    if len(links) != 1:
        return False
    link = links[0]

    return link.get_text(strip=True) == component.get_text(strip=True)


def get_link_texts(component):
    return [get_text_content(link) for link in component.find_all("a")]


def is_tweet(component):
    spans = component.find_all("span")
    return any(re.match(r"\d*\sRetweets", s.get_text()) for s in spans) and\
        any(re.match(r"\d*\sLikes", s.get_text()) for s in spans)
