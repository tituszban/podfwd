import imaplib
import email


class Inbox:
    def __init__(self, config, logger):
        self._server = config.get("EMAIL_SERVER")
        self.email_address = config.get("EMAIL_LOGIN")
        self._password = config.get("EMAIL_PASSWORD")
        self._disable_discard = config.get_bool("DISABLE_DISCARDING")
        self._logger = logger

        self._mail = None

    def login(self):
        self._mail = imaplib.IMAP4_SSL(self._server)
        self._mail.login(self.email_address, self._password)

    def discard_message(self, idx):
        if self._disable_discard:
            return

        _, data = self._mail.uid('STORE', idx, '+FLAGS', '(\\FLAGGED)')

    def get_messages(self):
        if self._mail is None:
            self.login()

        self._mail.select('"[Gmail]/All Mail"')

        _, ids = self._mail.uid('search', None, 'UNFLAGGED')
        ids = ids[0].decode().split()
        for idx in ids:
            _, messageRaw = self._mail.uid('fetch', idx, '(RFC822)')
            message = email.message_from_bytes(messageRaw[0][1])

            yield idx, message
