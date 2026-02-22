from email.message import Message
from email_exporter.config import Config
from typing import Iterator, Tuple, Union
from logging import Logger
import imaplib
import email
import re
from .inbox_abc import InboxABC


class GmailInbox(InboxABC):
    def __init__(self, config: Config, logger: Logger) -> None:
        self._server = config.get("EMAIL_SERVER")
        self._email_address = config.get("EMAIL_LOGIN")
        self._password = config.get("EMAIL_PASSWORD")
        self._disable_discard = config.get_bool("DISABLE_DISCARDING")
        self._logger = logger

        self._mail: Union[imaplib.IMAP4_SSL, None] = None

    def _login(self):
        server = imaplib.IMAP4_SSL(self._server)
        server.login(self.email_address, self._password)
        return server

    @property
    def email_address(self):
        return self._email_address

    def discard_message(self, idx):
        if self._disable_discard:
            return

        _ = self._ensure_success(self._mail.uid('STORE', idx, '+FLAGS', '(\\FLAGGED)'))

    def _ensure_success(self, action_result, success="OK"):
        status, result = action_result
        if status != success:
            raise Exception(f"Inbox returned not OK status: {status}; {action_result}")
        return result

    def _get_all_mail_folder(self):
        result = self._ensure_success(self._mail.list())

        result_list = list(map(lambda b: b.decode(), result))
        inbox_folder_re = re.compile(r"^\((?P<tags>(\\\w*\s?)*)\)\s\"/\"\s(?P<name>\".*\")$")
        folder_matches = list(map(inbox_folder_re.match, result_list))
        folders = list(map(
            lambda m: (
                tuple(map(lambda tag: tag.lstrip("\\").lower(), m.group("tags").split())),
                m.group("name")),
            folder_matches))

        all_folder = list(filter(lambda folder: "all" in folder[0], folders))

        if len(all_folder) <= 0:
            raise Exception("No folder found with 'All' tag")
        if len(all_folder) > 1:
            raise Exception("More than one folder found with 'All' tag")

        return all_folder[0][1]

    def get_messages(self, search_criteria: str = 'UNFLAGGED') -> Iterator[Tuple[int, Message]]:
        if self._mail is None:
            self._mail = self._login()

        all_folder = self._get_all_mail_folder()

        self._ensure_success(self._mail.select(all_folder))

        ids = self._ensure_success(self._mail.uid('search', None, search_criteria))  # type: ignore
        ids = ids[0].decode().split()
        for idx in ids:
            messageRaw = self._ensure_success(self._mail.uid('fetch', idx, '(RFC822)'))
            message = email.message_from_bytes(messageRaw[0][1])

            yield idx, message
