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
