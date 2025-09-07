import os

TG_TOKEN = os.getenv("TG_TOKEN")
TARGET_CHAT_ID = int(os.getenv("TARGET_CHAT_ID", "0"))
NEWS_INTERVAL_MIN = int(os.getenv("NEWS_INTERVAL_MIN", "30"))
TZ = os.getenv("TZ", "Europe/Moscow")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q4_K_M")

# Публичные RSS-каналы (пример). Замените на свои источники.
RSS_FEEDS = [
    "https://www.reuters.com/rss/worldNews",
    "https://www.reuters.com/finance/markets/commodities/rss",
    "https://www.sciencedaily.com/rss/top.xml",
]
