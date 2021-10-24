from email_exporter.config import Config
from email_exporter.inbox import Inbox
from logging import Logger
import re
import email
from bs4 import BeautifulSoup
from .inbox_item import InboxItem


class InboxProcessor:
    def __init__(self, config: Config, logger: Logger, inbox: Inbox):
        self._logger = logger
        self._inbox = inbox

    def _decode_header(self, header):
        default_charset = "utf-8"
        dh = email.header.decode_header(header)
        return ''.join(t.decode(e or default_charset) if type(t) == bytes else t for t, e in dh)

    def _remove_fwd(self, subject):
        prefixes = ["Fwd: ", "FW: "]
        for prefix in prefixes:
            if subject.startswith(prefix):
                subject = subject[len(prefix):]
        return subject

    def _get_message_data(self, message):
        subject = self._remove_fwd(self._decode_header(message["Subject"]))
        sender = self._decode_header(message["From"])
        recipient = self._decode_header(message["To"])
        date = self._decode_header(message["Date"])

        if (match := re.match(r".*<(?P<email>.*)>.*", sender)):
            sender = match.group("email")
        if (match := re.match(r".*<(?P<email>.*)>.*", recipient)):
            recipient = match.group("email")

        return subject, sender, recipient, date

    def _identify_participants(self, sender, recipient, mime):
        if recipient != self._inbox.email_address:
            return (recipient, sender)

        if (res := re.findall(r"From:.*<\s*(?P<email>.*)>", mime)):
            return (sender, res[0])

        return (sender, None)

    def _get_payload(self, message):
        if message.is_multipart():
            for m in message.get_payload():
                yield from self._get_payload(m)
        else:
            yield message.get_payload(decode=True)

    def _to_soup(self, raw):
        soup = BeautifulSoup(raw, 'html.parser')
        if soup.find("p") is None:
            return None
        return soup

    def _try_decode(self, payload):
        encodings = ("utf-8", "windows-1252")
        errors = []
        for encoding in encodings:
            try:
                return payload.decode(encoding), encoding
            except UnicodeDecodeError as e:
                errors.append(str(e))
        raise UnicodeDecodeError(
            "None of the known encodings were able to decode this payload; {}".format('; '.join(errors)))

    def _process_email(self, message):
        subject, sender, recipient, date = self._get_message_data(message)
        mime = ""
        html = ""
        soup = None

        for i, payload in enumerate(self._get_payload(message)):
            decode, _ = self._try_decode(payload)
            try_soup = self._to_soup(decode)
            if try_soup is None:
                mime = decode
            else:
                html = decode
                soup = try_soup

        addresses = self._identify_participants(sender, recipient, mime)

        return InboxItem(subject, date, html, mime, soup, addresses)

    def process_inbox(self, callback):
        self._logger.info("Processing inbox")
        for idx, message in self._inbox.get_messages():
            self._logger.info(f"Processing email {idx}")
            inbox_item = self._process_email(message)
            self._logger.info(f"Email {idx} processed: {inbox_item}")

            discard_message = False
            try:
                discard_message = callback(inbox_item)
            except Exception:
                self._logger.exception(
                    f"While processing email {idx}, an exception occured"
                )

            if discard_message:
                self._logger.info(f"Discarding message {idx}")
                self._inbox.discard_message(idx)
