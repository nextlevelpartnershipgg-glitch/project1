import os, httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
MODEL = os.getenv("LLM_MODEL", "llama3.1:8b-instruct-q4_K_M")

SYSTEM_PROMPT = """Ты редактор новостей Telegram.
Стиль: официальный, научный, без оценочных суждений.
Пиши ТОЛЬКО на основе переданных фактов (без домыслов).
Формат:
1) Заголовок (до 80 символов).
2) 2–5 кратких тезисов (каждый с новой строки).
3) Строка контекста/метрика, если есть.
4) Источники: кратко названия/URL.
Язык: русский.
"""

def build_user_prompt(facts: str, sources: list[str]) -> str:
    src = "\n".join(sources) if sources else ""
    return f"""Факты для новости:
{facts}

Источники:
{src}

Собери итоговый пост строго по формату. Не добавляй фактов, которых нет во входных данных."""

async def make_news_post(facts: str, sources: list[str]) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role":"system","content":SYSTEM_PROMPT},
            {"role":"user","content":build_user_prompt(facts, sources)}
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 4096}
    }
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(f"{OLLAMA_URL}/v1/chat/completions", json=payload)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
