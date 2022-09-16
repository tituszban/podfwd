from typing import Tuple, Union
from bs4 import BeautifulSoup


class InboxItem:
    def __init__(self,
                 subject: str,
                 date: str,
                 html: str,
                 mime: str,
                 soup: BeautifulSoup,
                 addresses: Tuple[str, Union[str, None]]):
        self.title = subject
        self.date = date
        self.html = html
        self.mime = mime
        self.soup = soup
        self.owner = addresses[0]
        self.sender: str = addresses[1] or ""

    def __repr__(self):
        return f"InboxItem({self.title}, {self.date}, from={self.sender}, to={self.owner})"

    def __str__(self):
        return f"InboxItem({self.title}, from={self.sender}, to={self.owner})"
