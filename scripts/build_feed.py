import csv

import requests
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

DOIS_FILE = "data/dois.csv"
OUTPUT_FILE = "feed.xml"

def fetch_metadata(doi):
    r = requests.get(f"https://api.crossref.org/works/{doi}")
    r.raise_for_status()
    msg = r.json()["message"]
    return {
        "title": msg["title"][0],
        "link": msg["URL"],
        "authors": ", ".join([a.get("family", "") for a in msg.get("author", [])]),
        "date": msg["created"]["date-time"],
        "journal": msg.get("container-title", [""])[0],
    }

def create_feed(items):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "Bioinformatics Tools & Papers"
    SubElement(channel, "link").text = "https://adoni5.github.io/workflow-rss/"
    SubElement(channel, "description").text = "Curated bioinformatics papers and tools"

    for item in items:
        entry = SubElement(channel, "item")
        SubElement(entry, "title").text = item["title"]
        SubElement(entry, "link").text = item["link"]
        SubElement(entry, "description").text = f"{item['journal']} — {item['authors']}"
        SubElement(entry, "pubDate").text = datetime.strptime(item["date"], "%Y-%m-%dT%H:%M:%SZ").strftime("%a, %d %b %Y %H:%M:%S +0000")
        SubElement(entry, "category").text = item["workflow"]
        SubElement(entry, "type").text = item["category"]
        SubElement(entry, "guid", isPermaLink="true").text = item["link"]

    ElementTree(rss).write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)

def main():
    with open(DOIS_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        items = [({**fetch_metadata(entry["doi"])} | entry) for entry in reader]
    
    create_feed(items)

if __name__ == "__main__":
    main()
