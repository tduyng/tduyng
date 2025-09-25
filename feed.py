import logging
from typing import Any
import pathlib
import feedparser
import requests
import re
from datetime import datetime

DEFAULT_N = 8
DEFAULT_DATE_FORMAT = "%Y-%m-%d"

root = pathlib.Path(__file__).parent.resolve()


def normalize_url(url: str, base_url: str) -> str:
    if url.startswith(('http://', 'https://')):
        return url
    path = url.lstrip('/')
    return f"{base_url.rstrip('/')}/{path}"

def fetch_feed(url: str, base_url: str = "https://tduyng.com") -> list[dict[str, str]]:
    try:
        response = requests.get(url)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        if not feed.entries:
            logging.error("Malformed feed: no entries found")
            return []
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the feed: {e}")
        return []
    except Exception as e:
        logging.error(f"Error processing the feed: {e}")
        return []

    return [
        {
            "title": entry.title,
            "url": normalize_url(entry.link, base_url),
            "date": format_entry_date(entry),
        }
        for entry in feed.entries[:DEFAULT_N]
    ]


def format_feed_entry(entry: dict[str, str]) -> str:
    title = entry.get("title", "No Title")
    link = entry.get("url", "")
    date = entry.get("date", "")

    return f"[{title}]({link}) - {date}"


def format_entry_date(entry: Any, date_format: str = DEFAULT_DATE_FORMAT) -> str:
    if hasattr(entry, "published_parsed"):
        published_time = datetime(*entry.published_parsed[:6])
        return published_time.strftime(date_format)
    return ""


def replace_chunk(content, marker, chunk, inline=False):
    pattern = f"<!-- {marker} start -->.*<!-- {marker} end -->"
    r = re.compile(pattern, re.DOTALL)
    
    if not inline:
        chunk = f"\n{chunk}\n"
        
    return r.sub(f"<!-- {marker} start -->{chunk}<!-- {marker} end -->", content)


if __name__ == "__main__":
    readme = root / "README.md"
    feed_url = "https://tduyng.com/atom.xml"
    base_url = "https://tduyng.com"
    feeds = fetch_feed(feed_url, base_url)
    feeds_md = "\n\n".join([format_feed_entry(feed) for feed in feeds])
    readme_contents = readme.read_text()
    rewritten = replace_chunk(readme_contents, "blog", feeds_md)
    readme.write_text(rewritten)
    print(feeds_md)
