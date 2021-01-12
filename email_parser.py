import imaplib
import email
from bs4 import BeautifulSoup
from functools import reduce
from ssml_builder.core import Speech


def get_payload(message):
    if message.is_multipart():
        for m in message.get_payload():
            for p in get_payload(m):
                yield p
    else:
        yield message.get_payload(decode=True)


def tc_parser(raw):
    soup = BeautifulSoup(raw, 'html.parser')
    table = soup.find("table")

    if not table:   # Not html payload
        return

    def find_tds_with_p(root):
        for td in root.find_all("td"):
            p = td.find("p", recursive=False)
            if p is not None:
                yield td

    tds = list(find_tds_with_p(table))

    def decompose_content(td):
        def get_text_content(n):
            return reduce(
                lambda txt, c: txt.replace(*c),
                [
                    ("\n", ""), ("\r", ""),
                    ("—", "-"), ("\xa0", " "), ("–", "-"),
                    ("”", '"'), ("“", '"'),
                    ("‘", "'"), ("’", "'"),
                    ("…", "...")
                ],
                n.get_text()).strip()

        for child in td:
            if child == "\n":
                continue

            if child.name == "ul":
                for li in child.find_all("li"):
                    yield li.name, get_text_content(li)
            else:
                yield child.name, get_text_content(child)

    def is_relevant(content):
        title_separator = "•"
        if any(title_separator in text for name, text in content):
            return False
        if any(name == "img" for name, text in content):
            return False
        if any(name == "h3" and "sponsored" in text.lower() for name, text in content):
            return False
        call_to_action = [
            "read more stories",
            "see more jobs",
            "privacy policy"
        ]
        if any(any(phrase in text.lower() for phrase in call_to_action) for name, text in content):
            return False
        ignored_sections = [
            "across the week",
            "around techcrunch",
            "equitypod",
        ]
        if any(any(phrase in text.lower() for phrase in ignored_sections) and "h" in name for name, text in content):
            return False
        return True

    def remove_lines(content):
        def remove_line(line):
            if "read more" in line.lower():
                return True
            if "membership program" in line.lower():
                return True
            if line == "":
                return True
            return False
        return [(name, text) for name, text in content if not remove_line(text)]

    def to_ssml(content):
        speech = Speech()

        for name, text in content:
            speech.add_text(text)
            if "h" in name:
                speech.pause(time="0.75s")
            else:
                speech.pause(time="0.5s")
        return speech

    for td in tds:
        content = list(decompose_content(td))
        if not is_relevant(content):
            continue
        content = remove_lines(content)

        ssml = to_ssml(content)

        yield ssml.speak()


def process_email(message):
    subject = message["Subject"].lstrip("Fwd: ")
    sender = message["From"]
    date = message["Date"]
    lines = []
    mime = ""
    html = ""

    for i, payload in enumerate(get_payload(message)):
        lines = list(tc_parser(payload))
        if len(lines) <= 0:
            mime = payload.decode("utf-8")
            continue
        html = payload.decode("utf-8")
        lines = lines
        
    return {
        "title": subject,
        "date": date,
        "description": html,
        "description2": mime,
        "content": lines
    }
        # with open(f"ssml/{subject}.txt", "w", encoding="utf-8") as f:
        #     f.write('\n'.join(lines))


def process_inbox():
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('autopod.tb@gmail.com', 'dvzmtxmwknumipzr')
    mail.select("inbox")

    typ, ids = mail.uid('search', None, 'ALL')
    ids = ids[0].decode().split()
    # print(ids)
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
