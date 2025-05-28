from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
from dp_handler.dp_class import Database


# переменные для работы
ADMIN_ID = config('ADMIN_ID')
API = config("API")
HOST = config("LHOST")
PORT = int(config("PORT"))
WEBHOOK_PATH = f'/{API}'
BASE_URL = config("URL")
USER = config('USER')
PASSWORD = config('PASSWORD')
DATABASE_LOCAL = config('DB_LOCAL')
DB_NAME = config('DB_NAME')

# dsn = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
db = Database(host=HOST,
              port=PORT,
              user=USER,
              password=PASSWORD,
              database=DB_NAME)
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
admins = [int(admin_id) for admin_id in config('ADMINS').split(',')]
 

bot = Bot(token=API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())