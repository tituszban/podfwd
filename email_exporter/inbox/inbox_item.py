class InboxItem:
    def __init__(self, subject, date, html, mime, soup, addresses):
        self.title = subject
        self.date = date
        self.html = html
        self.mime = mime
        self.soup = soup
        self.owner = addresses[0]
        self.sender = addresses[1]

    def __repr__(self):
        return f"InboxItem({self.title}, {self.date}, from={self.sender}, to={self.owner})"

    def __str__(self):
        return f"InboxItem({self.title}, from={self.sender}, to={self.owner})"
