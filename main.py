from email_parser import process_inbox
from t2s import TextToSpeech
from rss_gen import read, write, register_namespaces
import datetime

def find_max_id(item):
    return max([i["idx"] for i in item] + [0])


def old_items(items, lifetime_days=7):
    now = datetime.datetime.now()
    for item in items:
        date = datetime.datetime.strptime(item["date"], "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
        age = now - date
        print(age)
        if age > datetime.timedelta(days=lifetime_days):
            yield item



def main(request):
    # t2s = TextToSpeech("autopodcast", json="AutoPodcast-d352f15e5933.json")
    t2s = TextToSpeech("autopodcast")

    register_namespaces()
    xml = t2s.download_xml("feed.xml")
    root, items = read(xml)
    for item in old_items(items):
        t2s.delete_blob(f"{item['idx']}.mp3")

    inbox = list(process_inbox())

    start_id = find_max_id(items) + 1

    inbox = [{**inb, "idx": i + start_id} for i, inb in enumerate(inbox)]

    inbox = [
        {**i, "url": t2s.upload_lines(
            i["content"], f"{i['idx']}.mp3"
        )}
        for i in inbox]

    combined_items = [
        *[(i["title"], i["description"], i["url"], i["idx"], i["date"])
          for i in items],
        *[(i["title"], "", i["url"], i["idx"], i["date"]) for i in inbox]
    ]

    feed = write(root, combined_items)

    t2s.upload_xml("feed.xml", feed)

    return "Success"


# if __name__ == "__main__":
#     main(None)
