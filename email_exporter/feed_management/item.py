class Item:
    def __init__(self, title, description, date, url, idx):
        self.title = title
        self.description = description
        self.url = url
        self.idx = idx
        self.date = date

    @staticmethod
    def from_dict(d):
        return Item(
            d["title"],
            d["description"],
            d["date"],
            d["url"],
            d["id"]
        )

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "id": self.idx,
            "date": self.date
        }