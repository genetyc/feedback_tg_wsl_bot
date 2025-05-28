from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from os import environ
from dp_handler.dp_class import Database

# переменные для работы
ADMIN_ID = environ['ADMIN_ID']
API = environ["API"]
HOST = environ["LHOST"]
PORT = int(environ["PORT"])
USER = environ['USER']
PASSWORD = environ['PASSWORD']
DATABASE_LOCAL = environ['DB_LOCAL']
DB_NAME = environ['DB_NAME']
WEBHOOK_URL = environ['WEBHOOK_URL']
REMOTE_PORT = environ['REMOTE_PORT']

# dsn = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
db = Database(host=HOST,
              port=PORT,
              user=USER,
              password=PASSWORD,
              database=DB_NAME)
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
admins = [int(admin_id) for admin_id in environ['ADMINS'].split(',')]
 

bot = Bot(token=API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())