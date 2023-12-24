import io
import aiogram
import logging
import asyncio
from aiogram import Bot, Dispatcher, F, Router, types, html
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from typing import Any, Dict

from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from config import TOKEN
from utils import Form
from messages import MESSAGES


bot = Bot(token=TOKEN)
dp = Dispatcher()
data = None

#dp.middleware.setup(LoggingMiddleware())
my_router = Router(name= __name__)

@my_router.message(Command("start"))
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'])

@my_router.message(Command("help"))
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'])
