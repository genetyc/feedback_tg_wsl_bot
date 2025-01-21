from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from decouple import config

# переменные для работы
ADMIN_ID = config('ADMIN_ID')
API = config("API")
HOST = config("HOST")
PORT = int(config("PORT"))
WEBHOOK_PATH = f'/{API}'
BASE_URL = config("URL")
 
# инициализируем бота и диспетчера для работы с ним
bot = Bot(token=API, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()