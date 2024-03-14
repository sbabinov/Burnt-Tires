import asyncio
import concurrent.futures
import sqlite3

from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config
from database import Database, ServiceDataBase


# бот
bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)

# бд
# connection = sqlite3.connect('server.db')
# cursor = connection.cursor()
db = Database('database/main.db')
sdb = ServiceDataBase(config.SERVICE_DB_PATH)

# машина состояний
storage = MemoryStorage()

# диспетчер
dp = Dispatcher(bot, storage=storage)

# основной цикл
loop = asyncio.get_event_loop()
thread_pool = concurrent.futures.ThreadPoolExecutor()
proccess_pool = concurrent.futures.ProcessPoolExecutor()
