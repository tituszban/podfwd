from .parser_abc import ParserABC
from .content_item import ContentItem
from ssml_builder.core import Speech
import bleach

class TcParser(ParserABC):
    def __init__(self, logger):
        self._logger = logger

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
                    yield ContentItem.to_item(child)

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

        def to_ssml(content):
            speech = Speech()

            for c in content:
                speech.add_text(c.text)
                if "h" in c.name:
                    speech.pause(time="0.75s")
                else:
                    speech.pause(time="0.5s")
            return speech

        def clean_component(content):
            removed_attributes = ["class", "id", "name", "style"]
            components = []
            for c in content:
                components.append(bleach.clean(
                    str(c.component),
                    attributes=["href", "target", "alt", "src"],
                    tags=bleach.sanitizer.ALLOWED_TAGS + ["a", "img", "p", "h1", "h2", "h3", "h4", "span"]
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

            ssml = to_ssml(content)
            ssmls.append(ssml.speak())
            desc = clean_component(content)
            descriptions.append(desc)

        return ssmls, descriptions, select_voice()
