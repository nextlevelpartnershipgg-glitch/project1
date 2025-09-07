import datetime as dt
import feedparser

def fetch_rss_items(url: str, since: dt.datetime) -> list[dict]:
    d = feedparser.parse(url)
    items = []
    for e in d.entries:
        pub = None
        if getattr(e, "published_parsed", None):
            pub = dt.datetime(*e.published_parsed[:6], tzinfo=dt.timezone.utc)
        title = getattr(e, "title", "").strip()
        link = getattr(e, "link", "").strip()
        summary = getattr(e, "summary", "").strip()
        if pub is not None and since is not None and pub < since:
            continue
        if not title and not summary:
            continue
        items.append({"title": title, "link": link, "summary": summary, "published_at": pub})
    return items
