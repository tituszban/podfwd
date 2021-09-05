import imaplib
import email
from .inbox_abc import InboxABC


class GmailInbox(InboxABC):
    def __init__(self, config, logger):
        self._server = config.get("EMAIL_SERVER")
        self._email_address = config.get("EMAIL_LOGIN")
        self._password = config.get("EMAIL_PASSWORD")
        self._disable_discard = config.get_bool("DISABLE_DISCARDING")
        self._logger = logger

        self._mail = None

    def _login(self):
        self._mail = imaplib.IMAP4_SSL(self._server)
        self._mail.login(self.email_address, self._password)

    @property
    def email_address(self):
        return self._email_address

    def discard_message(self, idx):
        if self._disable_discard:
            return

        _, data = self._mail.uid('STORE', idx, '+FLAGS', '(\\FLAGGED)')

    def get_messages(self):
        if self._mail is None:
            self._login()

        self._mail.select('"[Gmail]/All mail"')

        _, ids = self._mail.uid('search', None, 'UNFLAGGED')
        ids = ids[0].decode().split()
        for idx in ids:
            _, messageRaw = self._mail.uid('fetch', idx, '(RFC822)')
            message = email.message_from_bytes(messageRaw[0][1])

            yield idx, message
