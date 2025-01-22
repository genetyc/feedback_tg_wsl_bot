from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
#from dp_handler.dp_class import PostgresHandler


# переменные для работы
ADMIN_ID = config('ADMIN_ID')
API = config("API")
HOST = config("HOST")
PORT = int(config("PORT"))
WEBHOOK_PATH = f'/{API}'
BASE_URL = config("URL")


#pg_db = PostgresHandler(config('PG_LINK'))
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
admins = [config('ADMIN_ID')]
 
# инициализируем бота и диспетчера для работы с ним
bot = Bot(token=API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())