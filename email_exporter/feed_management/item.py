import datetime
import re


class FileInfo:
    def __init__(self, url=None, file_name=None, is_external=False, is_removed=False, **kwargs):
        self.url = url
        self.file_name = file_name if file_name is not None or url is None else url.split("/")[-1]
        self.is_external = is_external
        self.is_removed = is_removed

    @staticmethod
    def from_dict(d):
        return FileInfo(**d)

    def to_dict(self):
        return {
            "url": self.url,
            "file_name": self.file_name,
            "is_external": self.is_external,
            "is_removed": self.is_removed
        }


class Item:
    def __init__(self,
                 title=None,
                 description=None,
                 date=None,
                 url=None,
                 idx=None,
                 sender=None,
                 file_info=None,
                 created_date=None,
                 **kwargs):
        self.title = title
        self.description = description
        self._url = url
        self.idx = idx
        self.date = date
        self.sender = sender
        self.created_date = created_date
        self.file_info = FileInfo(url) if url is not None else file_info

    @staticmethod
    def from_dict(d):
        return Item(**{
            **d,
            "idx": d.get("id", None),
            "file_info": FileInfo.from_dict(d.get("file_info", {}))
        })

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "id": self.idx,
            "date": self.date,
            "sender": self.sender,
            "file_info": self.file_info.to_dict() if self.file_info is not None else self.file_info,
            "created_date": self.created_date,
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
                dt = datetime.datetime.strptime(date, f)
                return dt.replace(tzinfo=None)
            except ValueError as e:
                errors.append(str(e))
        raise ValueError(
            f"Unable to process date {self.date}: {';'.join(errors)}")
