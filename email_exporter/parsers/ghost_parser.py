from .item_emitter import ItemEmitter
from .content_item import ContentItem


class GhostItemEmitter(ItemEmitter):
    """
    Item emitter for Ghost-based newsletters like Platformer.

    The email structure typically has:
    - A header table with site-info, post-title, feature-image
    - A main content area in a td with class "post-content-sans-serif"
    - Content marked with <!-- POST CONTENT START --> and <!-- POST CONTENT END --> comments
    - Footer with feedback buttons, footer text, and "Powered by Ghost" badge

    Elements to filter out:
    - kg-visibility-wrapper: promotional content wrappers
    - kg-cta-card: call-to-action cards with upgrade buttons
    - kg-paywall: paywall sections
    - kg-hr-card: horizontal rule dividers
    - kg-button-card: button cards with CTAs
    - feedback-buttons: comment/share buttons
    - footer, footer-powered: footer sections
    """

    def get_items(self, inbox_item):
        # Find the post content section - Ghost uses "post-content-sans-serif" class
        post_content = inbox_item.soup.find("td", class_="post-content-sans-serif")

        if post_content:
            yield from self._get_items_from_container(post_content)
            return

        # Fallback: try to find content by looking for partial class match
        post_content = inbox_item.soup.find("td", class_=lambda c: c and "post-content" in str(c))

        if post_content:
            yield from self._get_items_from_container(post_content)
            return

        # Last resort: look for the main wrapper with data-testid
        content_table = inbox_item.soup.find("table", attrs={"data-testid": "email-preview-content"})
        if content_table:
            post_content_row = content_table.find("tr", class_="post-content-row")
            if post_content_row:
                for td in post_content_row.find_all("td", recursive=False):
                    yield from self._get_items_from_container(td)

    def _get_items_from_container(self, container):
        """Extract content items from a container element."""
        for component in container.children:
            if component == "\n":
                continue
            yield ContentItem.to_item(component)
