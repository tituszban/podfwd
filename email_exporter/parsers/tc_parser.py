from .parser_abc import ParserABC
from .content_item import ContentItem
from ssml_builder.core import Speech
import bleach
from bs4 import NavigableString

class TcParser(ParserABC):
    def __init__(self, logger):
        self._logger = logger
        self.speech_limit = 5000

    def _split_long_content(self, content):
        def split_at_tag(l, tag):
            accum = []
            for c in l:
                if c.name == tag and len(accum) > 0:
                    yield accum
                    accum = []
                accum.append(c)
            yield accum
        
        split_tags = ["h1", "h2", "h3", "h4"]

        for tag in split_tags:
            if any([c.name == tag and i != 0 for i, c in enumerate(content)]):
                return list(split_at_tag(content, tag))

        if len(content) > 1:
            half = len(content) // 2
            return [content[:half], content[half:]]

        raise Exception("Failed to split long content")

    def _to_ssml(self, content):
        speech = Speech()

        for c in content:
            speech.add_text(c.text)
            if "h" in c.name:
                speech.pause(time="0.75s")
            else:
                speech.pause(time="0.5s")
        text = speech.speak()
        if len(text) < self.speech_limit:
            return [text]

        sub_sections = self._split_long_content(content)
        
        return [part for section in sub_sections for part in self._to_ssml(section)]


    def parse(self, soup=None, title="", **kwargs):
        assert soup is not None, "Soup not provided"
        table = soup.find("table")

        def find_tds_with_p(root):
            for td in root.find_all("td"):
                p = td.find("p", recursive=False)
                if p is not None:
                    yield td

        tds = list(find_tds_with_p(table))

        def decompose_content(td):
            for child in td:
                if child == "\n":
                    continue

                if child.name == "ul":
                    for li in child.find_all("li"):
                        yield ContentItem.to_item(li)
                else:
                    if any(isinstance(c, NavigableString) and c.strip() != '' for c in child.children) or not any(c.name == "p" for c in child.children):
                        yield ContentItem.to_item(child)
                    else:
                        for c in child.children:
                            if isinstance(c, NavigableString) and c.strip() == "":
                                continue
                            yield ContentItem.to_item(c)

        def is_relevant(content):
            title_separator = "•"
            if any(title_separator in c.text for c in content):
                return False
            if any(c.name == "img" for c in content):
                return False
            if any(c.name == "h3" and "sponsored" in c.text.lower() for c in content):
                return False
            call_to_action = [
                "read more stories",
                "see more jobs",
                "privacy policy"
            ]
            if any(any(phrase in c.text.lower() for phrase in call_to_action) for c in content):
                return False
            ignored_sections = [
                "across the week",
                "around techcrunch",
                "equitypod",
            ]
            if any(any(phrase in c.text.lower() for phrase in ignored_sections) and "h" in c.name for c in content):
                return False
            return True

        def remove_lines(content):
            def remove_line(line):
                if "read more" in line.text.lower() and line.is_only_link:
                    return True
                if "membership program" in line.text.lower():
                    return True
                if line == "":
                    return True
                return False
            return [c for c in content if not remove_line(c)]

        

        def clean_component(content):
            removed_attributes = ["class", "id", "name", "style"]
            components = []
            for c in content:
                components.append(bleach.clean(
                    str(c.component),
                    attributes=["href", "target", "alt", "src"],
                    tags=bleach.sanitizer.ALLOWED_TAGS + ["a", "img", "p", "h1", "h2", "h3", "h4", "span", "br"]
                ))
            return '\n'.join(components)

        def select_voice():
            if "startups weekly" in title.lower():
                return "en-US-Wavenet-H"
            return None # use default

        ssmls = []
        descriptions = []

        for td in tds:
            content = list(decompose_content(td))
            if not is_relevant(content):
                continue
            content = remove_lines(content)

            ssmls += self._to_ssml(content)
            desc = clean_component(content)
            descriptions.append(desc)

        return ssmls, descriptions, select_voice()
