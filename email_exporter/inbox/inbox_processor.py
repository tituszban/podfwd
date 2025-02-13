from email.message import Message
from email_exporter.config import Config
from email_exporter.inbox import Inbox
from logging import Logger
import re
import email
from bs4 import BeautifulSoup
from .inbox_item import InboxItem
from typing import Callable, Iterator, Tuple, Union


class InboxProcessor:
    def __init__(self, config: Config, logger: Logger, inbox: Inbox):
        self._config = config
        self._logger = logger
        self._inbox = inbox

    def _decode_header(self, header: str) -> str:
        default_charset = "utf-8"
        dh = email.header.decode_header(header)
        return ''.join(
            str(t.decode(encoding or default_charset)) if t is bytes else str(t)
            for t, encoding in dh
        )

    def _remove_fwd(self, subject: str) -> str:
        prefixes = ["Fwd: ", "FW: "]
        for prefix in prefixes:
            if subject.startswith(prefix):
                subject = subject[len(prefix):]
        return subject

    def _get_message_data(self, message: Message) -> Tuple[str, str, str, str]:
        subject = self._remove_fwd(self._decode_header(message["Subject"]))
        sender = self._decode_header(message["From"])
        recipient = self._decode_header(message["To"])
        date = self._decode_header(message["Date"])

        if (match := re.match(r".*<(?P<email>.*)>.*", sender)):
            sender = match.group("email")
        if (match := re.match(r".*<(?P<email>.*)>.*", recipient)):
            recipient = match.group("email")

        return subject, sender, recipient, date

    def _identify_participants(self, sender: str, recipient: str, mime: str) -> Tuple[str, Union[str, None]]:
        if recipient != self._inbox.email_address:
            return (recipient, sender)

        if (res := re.findall(r"From:.*<\s*(?P<email>.*)>", mime)):
            return (sender, res[0])

        return (sender, None)

    def _get_payload(self, message: Message) -> Iterator[bytes]:
        if message.is_multipart():
            for m in message.get_payload():
                yield from self._get_payload(m)     # type: ignore
        else:
            yield message.get_payload(decode=True)  # type: ignore

    def _to_soup(self, raw: str) -> Union[BeautifulSoup, None]:
        soup = BeautifulSoup(raw, 'html.parser')
        if soup.find("p") is None:
            return None
        return soup

    def _try_decode(self, payload: bytes) -> Tuple[str, str]:
        encodings = ("utf-8", "windows-1252")
        errors = []
        for encoding in encodings:
            try:
                return payload.decode(encoding), encoding
            except UnicodeDecodeError as e:
                errors.append(str(e))
        raise RuntimeError(
            "None of the known encodings were able to decode this payload; {}".format('; '.join(errors)))

    def _process_email(self, message: Message) -> InboxItem:
        subject, sender, recipient, date = self._get_message_data(message)
        mime = ""
        html = ""
        soup: BeautifulSoup = None      # type: ignore

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

    def process_inbox(self, callback: Callable[[InboxItem], bool]) -> None:
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
