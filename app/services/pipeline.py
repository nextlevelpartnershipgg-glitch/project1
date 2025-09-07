import datetime as dt
from .rss import fetch_rss_items

def collect_facts(rss_feeds: list[str], hours_back: int = 6) -> tuple[str,list[str]]:
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours_back)
    snippets = []
    sources = []
    for url in rss_feeds:
        try:
            items = fetch_rss_items(url, since)
            for it in items[:8]:  # берём верхние из каждого фида
                title = it.get("title","")
                summary = it.get("summary","")
                if title or summary:
                    snippets.append(f"{title} — {summary}")
                    if it.get("link"):
                        sources.append(it["link"])
        except Exception as e:
            # молча пропускаем проблемные feed'ы
            continue
    facts = "\n".join(snippets[:12])  # не перекармливаем модель
    # убираем дубликаты источников
    uniq_sources = list(dict.fromkeys(sources))[:10]
    return facts, uniq_sources
