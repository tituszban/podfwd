from .parser_abc import ParserABC
from .item_emitter import ItemEmitter
from .content_item import ContentItem
from ssml_builder.core import Speech
import re


class SubstackItemEmitter(ItemEmitter):
    def get_items(self, content_item):
        post_components = content_item.soup.find_all("div", class_=re.compile(r"post$"))

        for post_component in post_components:
            for component in post_component.div.children:
                yield ContentItem.to_item(component)


class SubstackParser(ParserABC):
    def __init__(self, logger):
        self._logger = logger
        self.speech_limit = 5000

    def _find_ph_parents(self, root):
        parents = []
        for p in root.find_all(["p", "h1", "h2", "h3", "h4"]):
            parent = p.find_parent("div")
            all_parents = p.find_parents("div")
            if all(p not in parents for p in all_parents):
                parents.append(parent)
        return parents

    def _decompose_component(self, component):
        for child in component:
            if child == "\n":
                continue

            if child.name == "ul":
                for li in child.find_all("li"):
                    yield ContentItem.to_item(li)
            else:
                yield ContentItem.to_item(child)

    def _is_section_relevant(self, content):
        free_list = "become a paying subscriber"
        if any(free_list in c.text.lower() for c in content):
            return False
        copyright_symbol = "©"
        if any(copyright_symbol in c.text for c in content):
            return False
        return True

    def _remove_lines(self, content):
        def remove_line(c):
            if c.text == "":
                return True
            if c.is_only_link and c.text.startswith("http"):
                return True
            cta_words = ["subscribe", "subscribe now", "share", "give a gift subscription"]
            if any(cta == c.text.lower() for cta in cta_words):
                return True
            cta_start = ["find me", "learn more about", "share"]
            if any(c.text.lower().startswith(cta) for cta in cta_start):
                return True
            return False

        def remove_in_case_you_missed_list(ctnt):
            in_list = False
            for c in ctnt:
                if c.text.lower().startswith("in case you missed"):
                    in_list = True
                elif in_list and c.name == "li":
                    continue
                elif in_list and c.name != "li":
                    in_list = False
                    yield c
                else:
                    yield c

        def remove_references(ctnt):
            in_list = False
            for c in ctnt:
                if c.text.lower() == "references" and "h" in c.name:
                    in_list = True
                elif in_list and c.is_only_link:
                    continue
                elif in_list and not c.is_only_link:
                    in_list = False
                    yield c
                else:
                    yield c

        content = list(remove_in_case_you_missed_list(content))
        content = list(remove_references(content))

        return [c for c in content if not remove_line(c)]

    def _split_long_content(self, content):
        def split_at_tag(line, tag):
            accum = []
            for comp in line:
                if comp.name == tag and len(accum) > 0:
                    yield accum
                    accum = []
                accum.append(comp)
            yield accum

        def split_text(text, split_characters=("\n", ".", " ")):
            for ch in split_characters:
                if ch not in text:
                    continue
                split = text.split(ch)
                if len(split) < 1:
                    continue
                half = len(split) // 2
                return [
                    [ContentItem.to_item(ch.join(split[:half]))],
                    [ContentItem.to_item(ch.join(split[half:]))],
                ]

            return []

        split_tags = ["h1", "h2", "h3", "h4"]

        for tag in split_tags:
            if any([c.name == tag and i != 0 for i, c in enumerate(content)]):
                return list(split_at_tag(content, tag))

        if len(content) > 1:
            half = len(content) // 2
            return [content[:half], content[half:]]

        if len(text_split := split_text(content[0].text)) > 0:
            return text_split

        raise Exception("Failed to split long content")

    def _to_ssml(self, content):
        if len(content) <= 0:
            return []
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

    def parse(self, content_item):
        assert content_item.soup is not None, "Soup not provided"
        items = list(SubstackItemEmitter().get_items(content_item))

        table = content_item.soup.find("table")

        parents = self._find_ph_parents(table)

        ssmls = []
        descriptions = []       # TODO: Create link collection

        for p in parents:
            content = list(self._decompose_component(p))
            if not self._is_section_relevant(content):
                continue
            content = self._remove_lines(content)

            ssmls += self._to_ssml(content)

        return ssmls, descriptions
