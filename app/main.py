import asyncio, os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv

from .config import TG_TOKEN, TARGET_CHAT_ID, NEWS_INTERVAL_MIN, TZ, OLLAMA_URL, LLM_MODEL, RSS_FEEDS
from .services.pipeline import collect_facts
from .services.llm import make_news_post
from .services.images import make_news_cover

load_dotenv()

bot = Bot(TG_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone=TZ)

STATE = {"news_enabled": False}

HELP_TEXT = (
    "Команды:\n"
    "/start — справка и проверка\n"
    "/post <тезис> — разовый пост\n"
    "/news_on — включить автоленту\n"
    "/news_off — выключить автоленту\n"
    "/status — статус"
)

@dp.message(Command("start"))
async def cmd_start(msg: Message):
    info = (f"TARGET_CHAT_ID: {TARGET_CHAT_ID}\n"
            f"NEWS_INTERVAL_MIN: {NEWS_INTERVAL_MIN}\n"
            f"TZ: {TZ}\n"
            f"LLM: {LLM_MODEL} @ {OLLAMA_URL}") if msg.chat.type == "private" else ""
    await msg.answer("Бот запущен. " + ("\n"+info if info else "") + "\n\n" + HELP_TEXT)

@dp.message(Command("status"))
async def cmd_status(msg: Message):
    feeds = "\n".join(RSS_FEEDS)
    enabled = "включена" if STATE.get("news_enabled") else "выключена"
    await msg.answer(f"Автолента: {enabled}\nИнтервал: {NEWS_INTERVAL_MIN} мин\nИсточники:\n{feeds}")

@dp.message(F.text.startswith("/post"))
async def cmd_post(msg: Message):
    q = msg.text.removeprefix("/post").strip()
    if not q:
        await msg.answer("Формат: /post <тезис>")
        return
    facts = q  # для разового поста используем тезис как факт-описание
    try:
        text = await make_news_post(facts, [])
        headline = text.splitlines()[0] if text else "Новость"
        cover_path = make_news_cover(headline)
        photo = FSInputFile(cover_path)
        await bot.send_photo(chat_id=TARGET_CHAT_ID or msg.chat.id, photo=photo, caption=text)
    except Exception as e:
        await msg.answer(f"Ошибка генерации: {e}")

async def periodic_news():
    facts, sources = collect_facts(RSS_FEEDS, hours_back=6)
    if not facts:
        return
    text = await make_news_post(facts, sources)
    headline = text.splitlines()[0] if text else "Новость"
    trend = "down" if any(w in text.lower() for w in ["паден", "снижен", "снижение", "минус"]) else None
    cover_path = make_news_cover(headline, trend=trend)
    photo = FSInputFile(cover_path)
    await bot.send_photo(chat_id=TARGET_CHAT_ID, photo=photo, caption=text)

@dp.message(Command("news_on"))
async def cmd_news_on(msg: Message):
    if not scheduler.get_jobs():
        scheduler.add_job(periodic_news, IntervalTrigger(minutes=NEWS_INTERVAL_MIN))
        scheduler.start()
    STATE["news_enabled"] = True
    await msg.answer("Автолента включена. Новости будут публиковаться автоматически.")

@dp.message(Command("news_off"))
async def cmd_news_off(msg: Message):
    for j in scheduler.get_jobs():
        scheduler.remove_job(j.id)
    STATE["news_enabled"] = False
    await msg.answer("Автолента выключена.")


@dp.message(Command("id"))
async def cmd_id(msg: Message):
    await msg.answer(f"chat_id: {msg.chat.id}")

# Для каналов
@dp.channel_post(Command("id"))
async def ch_id(msg: Message):
    await bot.send_message(chat_id=msg.chat.id, text=f"channel_id: {msg.chat.id}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
