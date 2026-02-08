from .item_emitter import ItemEmitter
from .content_item import ContentItem


class MailgunItemEmitter(ItemEmitter):
    """
    Item emitter for mailgun-based newsletters like Cautious Optimism.

    The email structure typically has:
    - A main table with nested tables for layout
    - A td with class "post-content" containing the article content
    - Headers, paragraphs, lists, blockquotes, and images as content
    """

    def get_items(self, inbox_item):
        # Find the post content section
        post_content = inbox_item.soup.find("td", class_="post-content")

        if post_content:
            yield from self._get_items_from_container(post_content)
            return

        # Fallback: try to find content by looking at the main structure
        # Some mailgun templates might have slightly different class names
        post_content = inbox_item.soup.find("td", class_=lambda c: c and "post-content" in c)

        if post_content:
            yield from self._get_items_from_container(post_content)
            return

        # Last resort: look for the main content div
        content_div = inbox_item.soup.find("div", style=lambda s: s and "max-width: 550px" in s)
        if content_div:
            for table in content_div.find_all("table", recursive=False):
                tbody = table.find("tbody")
                if tbody:
                    for tr in tbody.find_all("tr", recursive=False):
                        for td in tr.find_all("td", recursive=False):
                            yield from self._get_items_from_container(td)

    def _get_items_from_container(self, container):
        """Extract content items from a container element."""
        for component in container.children:
            if component == "\n":
                continue
            yield ContentItem.to_item(component)
