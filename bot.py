from urllib.parse import urljoin
import os
import subprocess
import time
import speech_recognition as sr
import typing as tp
from emoji import emojize
from aiohttp import ClientSession
import asyncio
import config

from aiogram import Bot, types
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import bold, code, italic, text
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram import F
from llm import LLM

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']


model = LLM()

telegram_bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def recommend_anime(message: types.Message) -> None:
    await message.reply(await model.generate(f"{config.RECOMMENDATION_PROMPT} {message.text}"))


async def main():
    print("Starting bot")
    await dp.start_polling(telegram_bot)

if __name__ == "__main__":
    asyncio.run(main())