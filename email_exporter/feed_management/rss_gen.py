import lxml.etree as ET
import datetime
import time
from email import utils

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "creativeCommons": "http://backend.userland.com/creativeCommonsRssModule",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "sy": "http://purl.org/rss/1.0/modules/syndication/",
    "rawvoice": "http://www.rawvoice.com/rawvoiceRssModule/",
    "googleplay": "http://www.google.com/schemas/play-podcasts/1.0"
}


def get_current_date_formatted():
    nowdt = datetime.datetime.now()
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    return utils.formatdate(nowtimestamp)


def add_subelement(parent, tag, text="", attr={}):
    if ":" in tag:
        s = tag.split(":")
        n = NAMESPACES[s[0]]
        tag = "{" + n + "}" + s[1]
    e = ET.SubElement(parent, tag, attrib=attr, nsmap=NAMESPACES)
    if text != "":
        e.text = text
    return e


def create_item_from_scratch(parent, item_content, author="PODFWD", keywords=("PODFWD",), block=True):
    item = ET.SubElement(parent, "item", nsmap=NAMESPACES)
    c_desc = ET.CDATA(item_content.description)
    item_url = item_content.file_info.url

    fields = (
        ("title", item_content.title, {}),
        ("itunes:title", item_content.title, {}),
        ("itunes:episodeType", "full", {}),
        ("pubDate", item_content.date, {}),
        ("itunes:episode", str(item_content.idx), {}),
        ("itunes:author", author, {}),
        ("category", "newsletters", {}),
        ("itunes:explicit", "clean", {}),
        ("itunes:subtitle", item_content.title, {}),
        ("itunes:keywords", ','.join(keywords), {}),
        ("googleplay:block", "yes" if block else "no", {}),
        ("itunes:block", "Yes" if block else "No", {}),
        ("description", c_desc, {}),
        ("itunes:summary", c_desc, {}),
        ("content:encoded", c_desc, {}),
        ("guid", item_url, {"isPermaLink": "false"}),
        ("enclosure", "", {"url": item_url, "length": "0", "type": "audio/mpeg"})
    )
    for tag, text, attr in fields:
        add_subelement(item, tag, text, attr)

    content = add_subelement(item, "media:content", "", {
        "url": item_url,
        "type": "audio/mpeg",
        "medium": "audio",
    })

    content_fields = (
        ("media:title", item_content.title, {"type": "plain"}),
        ("media:description", item_content.title, {"type": "plain"}),
        ("media:keywords", ','.join(keywords), {}),
        ("media:rating", "nonadult", {"scheme": "urn:simple"}),
        ("media:rating", "tv-g", {"scheme": "urn:v-chip"}),
        ("media:category", "IAB19", {"scheme": "urn:iab:categories", "label": "Technology"})
    )
    for tag, text, attr in content_fields:
        add_subelement(content, tag, text, attr)


def add_category(channel, category):
    s = category.split(":")
    root = channel
    for cat in s:
        root = add_subelement(root, "itunes:category", attr={"text": cat})


def generate_feed(feed):

    root = ET.Element("rss", nsmap=NAMESPACES)
    channel = ET.SubElement(root, "channel", nsmap=NAMESPACES)

    ts = get_current_date_formatted()

    author = feed.branding.author
    block = feed.block
    link = feed.branding.link
    email = feed.branding.email
    keywords = feed.branding.keywords
    subtitle = feed.branding.subtitle
    summary = feed.branding.summary
    # https://www.podcastinsights.com/itunes-podcast-categories/
    categories = feed.branding.categories
    logo_url = feed.branding.logo.url
    logo_size = feed.branding.logo.size
    feed_url = f"https://storage.googleapis.com/{feed.bucket_name}/{feed.feed_file_name}"

    channel_fields = (
        ("title", "PODFWD", {}),
        ("link", link, {}),
        ("generator", "rss_gen", {}),
        ("docs", "http://blogs.law.harvard.edu/tech/rss", {}),
        ("language", "en-US", {}),
        ("copyright", author, {}),
        ("ttl", str(720), {}),
        ("sy:updatePeriod", "daily", {}),
        ("sy:updateFrequency", str(1), {}),
        ("lastBuildDate", ts, {}),
        ("pubDate", ts, {}),
        ("rawvoice:frequency", "daily", {}),
        ("rawvoice:location", "London, UK", {}),
        ("itunes:type", "episodic", {}),
        ("itunes:author", author, {}),
        ("itunes:subtitle", subtitle, {}),
        ("itunes:summary", summary, {}),
        ("description", summary, {}),
        ("itunes:keywords", ",".join(keywords), {}),
        ("rawvoice:rating", "tv-g", {"tv": "tv-g"}),
        ("itunes:explicit", "clean", {}),
        ("googleplay:block", "yes" if block else "no", {}),
        ("itunes:block", "Yes" if block else "No", {}),
    )
    for tag, text, attr in channel_fields:
        add_subelement(channel, tag, text, attr)

    owner = add_subelement(channel, "itunes:owner")
    add_subelement(owner, "itunes:name", author)
    add_subelement(owner, "itunes:email", email)

    for category in categories:
        add_category(channel, category)

    image = add_subelement(channel, "image")
    add_subelement(image, "title", author)
    add_subelement(image, "url", logo_url)
    add_subelement(image, "link", link)
    add_subelement(image, "width", str(logo_size[0]))
    add_subelement(image, "height", str(logo_size[1]))

    add_subelement(channel, "itunes:image", attr={"href": logo_url})
    add_subelement(channel, "itunes:new-feed-url", feed_url)
    add_subelement(channel, "rawvoice:subscribe", attr={"feed": feed_url, "html": link})
    add_subelement(channel, "atom:link", attr={"href": feed_url, "type": "application/rss+xml", "rel": "self"})

    for item in feed.items:
        if item.file_info.is_removed:
            continue
        create_item_from_scratch(channel, item, author=author, keywords=keywords, block=block)

    return ET.tostring(root).decode("utf-8")
