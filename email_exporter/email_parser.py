import re
import imaplib
import email
from bs4 import BeautifulSoup


class Inbox:
    def __init__(self, config):
        self._server = config.get("EMAIL_SERVER")
        self._login = config.get("EMAIL_LOGIN")
        self._password = config.get("EMAIL_PASSWORD")

    def _get_message_data(self, message):
        subject = message["Subject"].lstrip("Fwd: ")
        sender = message["From"]
        date = message["Date"]

        if (match := re.match(r".*<(?P<email>.*)>.*", sender)):
            sender = match.group("email")

        return subject, sender, date

    def _get_payload(self, message):
        if message.is_multipart():
            for m in message.get_payload():
                for p in self._get_payload(m):
                    yield p
        else:
            yield message.get_payload(decode=True)

    def _to_soup(self, raw):
        soup = BeautifulSoup(raw, 'html.parser')
        if soup.find("p") is None:
            return None
        return soup

    def _process_email(self, message):
        subject, sender, date = self._get_message_data(message)
        mime = ""
        html = ""
        soup = None

        for i, payload in enumerate(self._get_payload(message)):
            soup = self._to_soup(payload)
            if soup is None:
                mime = payload.decode("utf-8")
                continue
            html = payload.decode("utf-8")

        return sender, {
            "title": subject,
            "date": date,
            "html": html,
            "mime": mime,
            "soup": soup
        }

    def process_inbox(self, callback):
        mail = imaplib.IMAP4_SSL(self._server)
        mail.login(self._login, self._password)
        mail.select("inbox")

        typ, ids = mail.uid('search', None, 'ALL')
        ids = ids[0].decode().split()
        for idx in ids:
            typ, messageRaw = mail.uid('fetch', idx, '(RFC822)')
            message = email.message_from_bytes(messageRaw[0][1])

            processed = self._process_email(message)

            discard_message = False
            try:
                discard_message = callback(*processed)
            except Exception as e:
                raise e

            if discard_message:
                mov, data = mail.uid('STORE', idx, '+FLAGS', '(\Deleted)')
                mail.expunge()
