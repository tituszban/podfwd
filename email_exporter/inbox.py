import re
import imaplib
import email
from bs4 import BeautifulSoup


class Inbox:
    def __init__(self, config, logger):
        self._server = config.get("EMAIL_SERVER")
        self._login = config.get("EMAIL_LOGIN")
        self._password = config.get("EMAIL_PASSWORD")
        self._logger = logger

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
        if recipient != self._login:
            return (recipient, sender)
        
        if (res := re.findall(r"From:.*<(?P<email>.*)>", mime)):
            return (sender, res[0])
        
        return (sender, None)

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

    def _try_decode(self, payload):
        encodings = ("utf-8", "windows-1252")
        errors = []
        for encoding in encodings:
            try:
                return payload.decode(encoding), encoding
            except UnicodeDecodeError as e:
                errors.append(str(e))
        raise UnicodeDecodeError("None of the known encodings were able to decode this payload; {}".format('; '.join(errors)))

    def _process_email(self, message):
        subject, sender, recipient, date = self._get_message_data(message)
        mime = ""
        html = ""
        soup = None

        for i, payload in enumerate(self._get_payload(message)):
            decode, _ = self._try_decode(payload)
            soup = self._to_soup(decode)
            if soup is None:
                mime = decode
            else:
                html = decode

        addresses = self._identify_participants(sender, recipient, mime)

        return addresses, {
            "title": subject,
            "date": date,
            "html": html,
            "mime": mime,
            "soup": soup
        }

    def process_inbox(self, callback):
        mail = imaplib.IMAP4_SSL(self._server)
        mail.login(self._login, self._password)
        mail.select('"[Gmail]/All Mail"')

        _, ids = mail.uid('search', None, 'UNFLAGGED')
        ids = ids[0].decode().split()
        for idx in ids:
            _, messageRaw = mail.uid('fetch', idx, '(RFC822)')
            message = email.message_from_bytes(messageRaw[0][1])

            processed = self._process_email(message)

            discard_message = False
            try:
                discard_message = callback(*processed)
            except Exception as e:
                self._logger.exception(
                    f"While processing email {idx}, an exception occured"
                )

            if discard_message:
                _, data = mail.uid('STORE', idx, '+FLAGS', '(\\FLAGGED)')
