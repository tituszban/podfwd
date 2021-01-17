import datetime
import re


class Item:
    def __init__(self, title=None, description=None, date=None, url=None, idx=None, sender=None, **kwargs):
        self.title = title
        self.description = description
        self.url = url
        self.idx = idx
        self.date = date
        self.sender = sender

    @staticmethod
    def from_dict(d):
        return Item(**{**d, "idx": d.get("id", None)})

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "id": self.idx,
            "date": self.date,
            "sender": self.sender
        }

    def try_get_date(self):
        formats = [
            "%a, %d %b %Y %H:%M:%S %z",
            "%a, %d %b %Y %H:%M:%S %z %Z",
        ]
        errors = []
        date = re.sub(r"\s*\(.*\)", "", self.date)
        for f in formats:
            try:
                return datetime.datetime.strptime(date, f)
            except ValueError as e:
                errors.append(str(e))
        raise ValueError(
            f"Unable to process date {self.date}: {';'.join(errors)}")

    @property
    def file_name(self):
        return f"{self.idx}.mp3"
