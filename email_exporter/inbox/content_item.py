class ContentItem:
    def __init__(self, subject, date, html, mime, soup, addresses):
        self.title = subject
        self.date = date
        self.html = html
        self.mime = mime
        self.soup = soup
        self.owner = addresses[0]
        self.sender = addresses[1]