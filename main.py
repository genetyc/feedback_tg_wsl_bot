import logging
import asyncio
import json
from aiogram.types import BotCommand, BotCommandScopeDefault
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from bot_create import bot, dp, BASE_URL, WEBHOOK_PATH, HOST, PORT, ADMIN_ID
from handlers.start import start_router

# Функция для проверки вебхука TODO - удалить после отладки
# async def print_webhook_info():
#     webhook_info = await bot.get_webhook_info()
#     print(webhook_info)

# Функция для установки командного меню для бота
async def set_commands():
    # Создаем список команд, которые будут доступны пользователям
    commands = [BotCommand(command='start', description='Старт')]
    # Устанавливаем эти команды как дефолтные для всех пользователей
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая будет вызвана при запуске бота TODO удалить все связанное с вебхуками - на время отладки буду использовать поллинг
async def on_startup() -> None:
    # Устанавливаем командное меню
    await set_commands()
    # Устанавливаем вебхук для приема сообщений через заданный URL
    # await bot.set_webhook(BASE_URL+WEBHOOK_PATH)
    # Отправляем сообщение администратору о том, что бот был запущен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')
    print("Bot is running...")
    # await print_webhook_info()


# Функция, которая будет вызвана при остановке бота
async def on_shutdown() -> None:
    # Отправляем сообщение администратору о том, что бот был остановлен
    await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
    # Удаляем вебхук и, при необходимости, очищаем ожидающие обновления
    # await bot.delete_webhook(drop_pending_updates=True)
    # Закрываем сессию бота, освобождая ресурсы
    await bot.session.close()


# Основная функция, которая запускает приложение
async def main() -> None:
    # Подключаем маршрутизатор (роутер) для обработки сообщений
    dp.include_router(start_router)

    # Регистрируем функцию, которая будет вызвана при старте бота
    dp.startup.register(on_startup)

    # Регистрируем функцию, которая будет вызвана при остановке бота
    dp.shutdown.register(on_shutdown)
    logging.basicConfig(level=logging.DEBUG)

    # Создаем веб-приложение на базе aiohttp
    # app = web.Application()

    # Настраиваем обработчик запросов для работы с вебхуком
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,  # Передаем диспетчер
    #     bot=bot  # Передаем объект бота
    # )
    # Регистрируем обработчик запросов на определенном пути
    # webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    # setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    #web.run_app(app, host=HOST, port=PORT)

    #asyncio.run(dp.start_polling(bot))
    await dp.start_polling(bot)


# Точка входа в программу
if __name__ == "__main__":
    # Настраиваем логирование (информация, предупреждения, ошибки) и выводим их в консоль
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)  # Создаем логгер для использования в других частях программы
    asyncio.run(main())  # Запускаем основную функцию