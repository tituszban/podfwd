import os
import email
from email.message import Message
from typing import Iterator, Tuple, Optional
from dataclasses import dataclass
import hashlib
import logging

from email_exporter.inbox import InboxItem, Inbox, InboxProcessor
from email_exporter.config import Config

from .storage import DevStorage


@dataclass
class EmailInfo:
    id: str
    subject: str
    sender: str
    date: str
    date_timestamp: float
    source: str
    path: Optional[str]
    is_starred: bool
    email_type: str

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "sender": self.sender,
            "date": self.date,
            "dateTimestamp": self.date_timestamp,
            "source": self.source,
            "isStarred": self.is_starred,
            "emailType": self.email_type
        }


class EmailLoader:
    GMAIL_SEARCHES = [
        ('UNFLAGGED', 'inbox'),
        ('X-GM-LABELS "Debug"', 'debug'),
        ('X-GM-LABELS "TestCase"', 'testcase'),
    ]

    def __init__(
        self,
        sources_folder: str,
        storage: DevStorage,
        config: Config,
        logger: logging.Logger
    ):
        self._sources_folder = sources_folder
        self._storage = storage
        self._config = config
        self._logger = logger
        self._email_cache: dict[str, Tuple[Message, str]] = {}
        self._inbox: Optional[Inbox] = None
        self._processor: Optional[InboxProcessor] = None

    def _get_inbox(self) -> Optional[Inbox]:
        if self._inbox is None:
            try:
                if not all([self._config.get("EMAIL_SERVER"), self._config.get("EMAIL_LOGIN"), self._config.get("EMAIL_PASSWORD")]):
                    self._logger.warning("Gmail config not available")
                    return None
                self._inbox = Inbox(self._config, self._logger)
            except Exception as e:
                self._logger.warning(f"Failed to create inbox: {e}")
                return None
        return self._inbox

    def _get_processor(self) -> Optional[InboxProcessor]:
        if self._processor is None:
            inbox = self._get_inbox()
            if inbox is None:
                return None
            self._processor = InboxProcessor(self._config, self._logger, inbox)
        return self._processor

    def _parse_date(self, date_str: str) -> Tuple[str, float]:
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.strftime("%Y-%m-%d %H:%M"), dt.timestamp()
        except Exception:
            return date_str, 0.0

    def _get_email_id(self, source: str, identifier: str) -> str:
        content = f"{source}:{identifier}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _extract_sender_from_message(self, message: Message) -> str:
        from_header = message.get("From", "")
        if "<" in from_header and ">" in from_header:
            return from_header.split("<")[1].split(">")[0]
        return from_header

    def _load_eml_files(self) -> Iterator[Tuple[EmailInfo, Message]]:
        if not os.path.exists(self._sources_folder):
            return
        for root, _, files in os.walk(self._sources_folder):
            for filename in files:
                if filename.endswith(".eml"):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, "rb") as f:
                            message = email.message_from_bytes(f.read())
                        email_id = self._get_email_id("eml", filepath)
                        date_str = message.get("Date", "")
                        date_formatted, date_ts = self._parse_date(date_str)
                        info = EmailInfo(
                            id=email_id,
                            subject=message.get("Subject", "(No Subject)"),
                            sender=self._extract_sender_from_message(message),
                            date=date_formatted,
                            date_timestamp=date_ts,
                            source="eml",
                            path=filepath,
                            is_starred=False,
                            email_type="eml"
                        )
                        self._email_cache[email_id] = (message, "eml")
                        yield info, message
                    except Exception as e:
                        self._logger.warning(f"Error loading {filepath}: {e}")
                        continue

    def _load_gmail_emails(self) -> Iterator[Tuple[EmailInfo, Message]]:
        inbox = self._get_inbox()
        if inbox is None:
            return
        seen_ids = set()
        for search_criteria, email_type in self.GMAIL_SEARCHES:
            try:
                for idx, message in inbox.get_messages(search_criteria):
                    if idx in seen_ids:
                        continue
                    seen_ids.add(idx)
                    email_id = self._get_email_id("gmail", str(idx))
                    date_str = message.get("Date", "")
                    date_formatted, date_ts = self._parse_date(date_str)
                    info = EmailInfo(
                        id=email_id,
                        subject=message.get("Subject", "(No Subject)"),
                        sender=self._extract_sender_from_message(message),
                        date=date_formatted,
                        date_timestamp=date_ts,
                        source="gmail",
                        path=None,
                        is_starred=False,
                        email_type=email_type
                    )
                    self._email_cache[email_id] = (message, str(idx))
                    yield info, message
            except Exception as e:
                self._logger.warning(f"Error searching for {search_criteria}: {e}")
                continue

    def get_all_emails(self) -> list[EmailInfo]:
        emails = []
        for info, _ in self._load_eml_files():
            emails.append(info)
        for info, _ in self._load_gmail_emails():
            emails.append(info)
        emails.sort(key=lambda e: e.date_timestamp, reverse=True)
        return emails

    def get_email(self, email_id: str) -> Optional[InboxItem]:
        if email_id not in self._email_cache:
            list(self._load_eml_files())
            list(self._load_gmail_emails())
        if email_id not in self._email_cache:
            return None
        message, _ = self._email_cache[email_id]
        processor = self._get_processor()
        if processor is not None:
            return processor.process_email(message)
        return self._message_to_inbox_item(message)

    def _message_to_inbox_item(self, message: Message) -> InboxItem:
        from bs4 import BeautifulSoup
        html_body = self._get_html_body(message)
        soup = BeautifulSoup(html_body, "html.parser") if html_body else None
        sender = self._extract_sender_from_message(message)
        recipient = message.get("To", "")
        if "<" in recipient and ">" in recipient:
            recipient = recipient.split("<")[1].split(">")[0]
        return InboxItem(
            subject=message.get("Subject", "(No Subject)"),
            date=message.get("Date", ""),
            html=html_body,
            mime=str(message),
            soup=soup,
            addresses=(recipient, sender)
        )

    def _get_html_body(self, message: Message) -> str:
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
        else:
            content_type = message.get_content_type()
            if content_type == "text/html":
                payload = message.get_payload(decode=True)
                charset = message.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
        return ""

    def get_raw_html(self, email_id: str) -> Optional[str]:
        if email_id not in self._email_cache:
            list(self._load_eml_files())
            list(self._load_gmail_emails())
        if email_id not in self._email_cache:
            return None
        message, _ = self._email_cache[email_id]
        return self._get_html_body(message)

    def mark_starred(self, email_id: str, starred: bool):
        self._storage.set(f"starred:{email_id}", starred)
