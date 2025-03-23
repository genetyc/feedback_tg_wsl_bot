import logging
import asyncio
import json
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot_create import bot, dp, ADMIN_ID, db

#from dp_handler.dp_class import connect_to_db
# Функция для проверки вебхука TODO - удалить после отладки
# async def print_webhook_info():
# #     webhook_info = await bot.get_webhook_info()
#     print(webhook_info)
# Функция для установки командного меню для бота
async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [BotCommand(command='start', description='Старт')]
    # Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая будет вызвана при запуске бота TODO удалить все связанное с вебхуками - на время отладки буду использовать поллинг
async def on_startup() -> None:
    global file
    # Устанавливаем командное меню
    await set_commands()
    # Устанавливаем вебхук для приема сообщений через заданный URL
    # await bot.set_webhook(BASE_URL+WEBHOOK_PATH)
    # Отправляем сообщение администратору о том, что бот был запущен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')
    print("Bot is running...")
    await db.connect()        

    # await print_webhook_info()


from handlers import survey, mini_survey, start
# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:
    # Отправляем сообщение администратору о том, что бот был остановлен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
    await db.close()
    
    # Удаляем вебхук и, при необходимости, очищаем ожидающие обновления
    # await bot.delete_webhook(drop_pending_updates=True)
    # Закрываем сессию бота, освобождая ресурсы

    #await pool.close()
    #print('Database access closed')
    await bot.session.close()


# Основная функция, которая запускает приложение
async def main() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    dp.include_router(start.start_router)
    dp.include_router(survey.survey_router)
    dp.include_router(mini_survey.mini_survey_router)

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)

# Точка входа в программу
if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #logger = logging.getLogger(__name__)  # Создаем логгер для использования в других частях программы
    asyncio.run(main())  # Запускаем основную функцию