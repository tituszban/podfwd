from functools import reduce


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
            n.get_text(" ", strip=True)).strip()

    @staticmethod
    def is_only_link(n):
        links = n.find_all("a")
        if len(links) != 1:
            return False
        link = links[0]

        return link.get_text() == n.get_text()

    @staticmethod
    def get_link_texts(n):
        return [TextContent.get_text_content(link) for link in n.find_all("a")]

    def __init__(self, component):
        self.component = component
        self.name = component.name
        self.text = TextContent.get_text_content(component)
        self.is_only_link = TextContent.is_only_link(component)
        self.links = TextContent.get_link_texts(component)
