import re
import imaplib
import email
from bs4 import BeautifulSoup


def get_message_data(message):
    subject = message["Subject"].lstrip("Fwd: ")
    sender = message["From"]
    date = message["Date"]

    if (match := re.match(r".*<(?P<email>.*)>.*", sender)):
        sender = match.group("email")

    return subject, sender, date


def get_payload(message):
    if message.is_multipart():
        for m in message.get_payload():
            for p in get_payload(m):
                yield p
    else:
        yield message.get_payload(decode=True)


def to_soup(raw):
    soup = BeautifulSoup(raw, 'html.parser')
    if soup.find("p") is None:
        return None
    return soup


def process_email(message):
    subject, sender, date = get_message_data(message)
    mime = ""
    html = ""
    soup = None

    for i, payload in enumerate(get_payload(message)):
        soup = to_soup(payload)
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


def process_inbox():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('autopod.tb@gmail.com', 'dvzmtxmwknumipzr')
    mail.select("inbox")

    typ, ids = mail.uid('search', None, 'ALL')
    ids = ids[0].decode().split()
    for idx in ids:
        typ, messageRaw = mail.uid('fetch', idx, '(RFC822)')
        message = email.message_from_bytes(messageRaw[0][1])

        yield process_email(message)

        mov, data = mail.uid('STORE', idx, '+FLAGS', '(\Deleted)')
        mail.expunge()


def main():
    result = list(process_inbox())
    print(result)


if __name__ == "__main__":
    main()
