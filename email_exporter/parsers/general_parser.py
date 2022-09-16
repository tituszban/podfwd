from .parser_abc import ParserABC
# from .content_item import ContentItem
from ssml import SpeechBuilder
# import bleach
# from bs4 import BeautifulSoup
from functools import reduce
from .parsed_item import ParsedItem


class GeneralParser(ParserABC):
    def __init__(self, logger):
        self._logger = logger
        self.speech_limit = 5000

    def _sanitise(self, text):
        return reduce(
            lambda txt, c: txt.replace(*c),
            [
                ("\n", ""), ("\r", ""),
                ("—", "-"), ("\xa0", " "), ("–", "-"),
                ("”", '"'), ("“", '"'),
                ("‘", "'"), ("’", "'"),
                ("…", "...")
            ],
            text).strip()

    def _remove_forward_header(self, lines):
        if "forward" not in lines[0].lower():
            return lines
        fwd_end = next(i for i, line in enumerate(lines) if line.lower().startswith("to:"))
        return lines[fwd_end + 3:]

    def _strip_mailchimp_view_in_browser(self, lines):
        return [line for line in lines if line.lower() != "view this email in your browser"]

    def _remove_after_copyright(self, lines):
        try:
            cpr_line = next(i for i, line in enumerate(lines) if line.lower().startswith("copyright"))
        except StopIteration:
            return lines

        return lines[:cpr_line]

    def _to_ssms(self, lines, headers):
        def build_speech(_lines):
            speech = SpeechBuilder()
            for line in _lines:
                if line in headers:
                    speech.pause(time="1.5s")
                else:
                    speech.pause(time="0.75s")
                speech.add_text(line)
            return speech

        last_built = 0
        for i, line in enumerate(lines):
            speech = build_speech(lines[last_built:i+1])
            if len(speech.speak()) > self.speech_limit:
                if last_built == i - 1:
                    raise Exception("Single section too long")

                yield build_speech(lines[last_built:i]).speak()
                last_built = i
        yield build_speech(lines[last_built:]).speak()

    def parse(self, content_item):
        assert content_item.soup is not None

        headers = [self._sanitise(text)
                   for item in content_item.soup.findAll(["h1", "h2", "h3", "h4", "h5", "h6"])
                   for text in item.get_text().split("\n")]

        all_text = [
            sanitised
            for item in content_item.soup.findAll(text=True)
            if (sanitised := self._sanitise(item)) != ""
        ]

        processors = [
            self._remove_forward_header,
            self._strip_mailchimp_view_in_browser,
            self._remove_after_copyright
        ]

        all_text = reduce(lambda lines, processor: processor(lines), processors, all_text)

        ssmls = list(self._to_ssms(all_text, headers))

        return ParsedItem(ssmls)
