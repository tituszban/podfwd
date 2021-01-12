from .parser_abc import ParserABC
from functools import reduce
from ssml_builder.core import Speech

class TextContent:
    @staticmethod
    def get_text_content(n):
        return reduce(
            lambda txt, c: txt.replace(*c),
            [
                ("\n", ""), ("\r", ""),
                ("—", "-"), ("\xa0", " "), ("–", "-"),
                ("”", '"'), ("“", '"'),
                ("‘", "'"), ("’", "'"),
                ("…", "...")
            ],
            n.get_text()).strip()

    def __init__(self, component):
        self.component = component
        self.name = component.name
        self.text = TextContent.get_text_content(component)


class TcParser(ParserABC):
    def __init__(self):
        pass

    def parse(self, soup):
        table = soup.find("table")

        def find_tds_with_p(root):
            for td in root.find_all("td"):
                p = td.find("p", recursive=False)
                if p is not None:
                    yield td

        tds = list(find_tds_with_p(table))

        def decompose_content(td):
            def get_text_content(n):
                return reduce(
                    lambda txt, c: txt.replace(*c),
                    [
                        ("\n", ""), ("\r", ""),
                        ("—", "-"), ("\xa0", " "), ("–", "-"),
                        ("”", '"'), ("“", '"'),
                        ("‘", "'"), ("’", "'"),
                        ("…", "...")
                    ],
                    n.get_text()).strip()

            for child in td:
                if child == "\n":
                    continue

                if child.name == "ul":
                    for li in child.find_all("li"):
                        yield TextContent(li)
                else:
                    yield TextContent(child)

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
                if "read more" in line.lower():
                    return True
                if "membership program" in line.lower():
                    return True
                if line == "":
                    return True
                return False
            return [c for c in content if not remove_line(c.text)]

        def to_ssml(content):
            speech = Speech()

            for c in content:
                speech.add_text(c.text)
                if "h" in c.name:
                    speech.pause(time="0.75s")
                else:
                    speech.pause(time="0.5s")
            return speech

        for td in tds:
            content = list(decompose_content(td))
            if not is_relevant(content):
                continue
            content = remove_lines(content)

            ssml = to_ssml(content)

            yield ssml.speak()