import lxml.etree as ET
import datetime
import time
from email import utils

item_template = """
<rss xmlns:atom="http://www.w3.org/2005/Atom"
	xmlns:media="http://search.yahoo.com/mrss/"
	xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
	xmlns:creativeCommons="http://backend.userland.com/creativeCommonsRssModule"
	xmlns:content="http://purl.org/rss/1.0/modules/content/"
	xmlns:sy="http://purl.org/rss/1.0/modules/syndication/"
    xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
	xmlns:rawvoice="http://www.rawvoice.com/rawvoiceRssModule/" version="2.0">
<item>
    <title></title>
    <itunes:title></itunes:title>
    <itunes:episodeType>full</itunes:episodeType>
    <pubDate></pubDate>
    <itunes:episode></itunes:episode>
    <itunes:author>TB</itunes:author>
    <category>Tech News</category>
    <itunes:explicit>clean</itunes:explicit>
    <itunes:subtitle></itunes:subtitle>
    <itunes:keywords>Autopod</itunes:keywords>
    <googleplay:block>yes</googleplay:block>
    <itunes:block>Yes</itunes:block>
    <description>
    </description>
    <itunes:summary>
    </itunes:summary>
    <content:encoded>
    </content:encoded>
    <guid isPermaLink="false"></guid>
    <enclosure url="" length="0" type="audio/mpeg"/>
    <media:content url="" type="audio/mpeg" medium="audio">
        <media:title type="plain"></media:title>
        <media:description type="plain"></media:description>
        <media:keywords>Autopod</media:keywords>
        <media:rating scheme="urn:simple">nonadult</media:rating>
        <media:rating scheme="urn:v-chip">tv-g</media:rating>
        <media:category scheme="urn:iab:categories" label="Technology">IAB19</media:category>
    </media:content>
</item>
</rss>
"""


def get_current_date_formatted():
    nowdt = datetime.datetime.now()
    nowtuple = nowdt.timetuple()
    nowtimestamp = time.mktime(nowtuple)
    return utils.formatdate(nowtimestamp)


def read(data):
    root = ET.fromstring(data)
    channel = root.find("channel")
    items = channel.findall("item")
    its = []
    # print(len(items))
    ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
    for item in items:
        channel.remove(item)
        its.append({
            "title": item.find('title', ns).text,
            "description": item.find("description", ns).text,
            "url": item.find("enclosure", ns).attrib["url"],
            "idx": int(item.find('itunes:episode', ns).text),
            "date": item.find("pubDate").text
        })

    return root, its


def create_item(title, description, url, idx, date):
    # print(title, url, idx, date)
    ns = {
        "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
        "media": "http://search.yahoo.com/mrss/",
        "content": "http://purl.org/rss/1.0/modules/content/"
    }

    c_desc = ET.CDATA(description)

    item = ET.fromstring(item_template).find("item")
    item.find("title", ns).text = title
    item.find("itunes:title", ns).text = title
    item.find("pubDate", ns).text = date
    item.find("itunes:episode", ns).text = str(idx)
    item.find("itunes:subtitle", ns).text = title
    item.find("description", ns).text = c_desc
    item.find("itunes:summary", ns).text = c_desc
    item.find("content:encoded", ns).text = c_desc
    item.find("guid", ns).text = url
    item.find("enclosure", ns).attrib["url"] = url
    content = item.find("media:content", ns)
    content.attrib["url"] = url
    content.find("media:title", ns).text = title
    content.find("media:description", ns).text = title
    return item


def register_namespaces():
    ET.register_namespace("atom", "http://www.w3.org/2005/Atom")
    ET.register_namespace("media", "http://search.yahoo.com/mrss/")
    ET.register_namespace(
        "itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    ET.register_namespace(
        "creativeCommons", "http://backend.userland.com/creativeCommonsRssModule")
    ET.register_namespace(
        "content", "http://purl.org/rss/1.0/modules/content/")
    ET.register_namespace("sy", "http://purl.org/rss/1.0/modules/syndication/")
    ET.register_namespace(
        "rawvoice", "http://www.rawvoice.com/rawvoiceRssModule/")


def write(current, items):
    channel = current.find("channel")

    ts = get_current_date_formatted()
    channel.find("lastBuildDate").text = ts
    channel.find("pubDate").text = ts

    for i in items:
        item = create_item(*i)
        channel.append(item)

    return ET.tostring(current).decode("utf-8")


def main():
    root, items = read("starting_feed.xml")
    write(root, items, 0, "feed.xml")


if __name__ == "__main__":
    main()
