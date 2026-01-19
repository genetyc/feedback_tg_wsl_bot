import logging
import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from bot_create import bot, dp, ADMIN_ID, db, WEBHOOK_URL, API, REMOTE_PORT


async def set_commands():
    logging.info("Setting bot commands...")
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())
    logging.info("Bot commands set.")


async def on_startup() -> None:
    # global file
    try:
        await set_commands()
        await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')
        await bot.delete_webhook()
        #await bot.set_webhook(WEBHOOK_PATH)
        logging.info("Setting webhook...")
        await bot.set_webhook(
            url=f"{WEBHOOK_URL}/{API}",
            drop_pending_updates=True
        )
        # print("Bot is running...")
        logging.info("Connecting to the database...")
        await db.connect()
        logging.info("Starting...")
    except Exception as e:
        logging.error(f"Error while launching: {e}")


async def on_shutdown() -> None:
    await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
    await bot.delete_webhook()
    await db.close()
    await bot.session.close()


from handlers import admin_panel, survey, mini_survey, start
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
async def main() -> None:
    logging.info("Including routers...")
    dp.include_router(start.start_router)
    dp.include_router(survey.survey_router)
    dp.include_router(mini_survey.mini_survey_router)
    dp.include_router(admin_panel.admin_router)
    logging.info("Startup and shutdown handlers registration...")
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    # await dp.start_polling(bot)
    logging.info("Starting webhook server...")
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot)
    webhook_requests_handler.register(app, path=f"/{API}")
    setup_application(app, dp, bot=bot)

    logging.info("Starting webhook site...")
    runner = web.AppRunner(app)
    await runner.setup()
    
    logging.info(f"Listening on remote port {REMOTE_PORT}...")
    site = web.TCPSite(runner, host="0.0.0.0", port=int(REMOTE_PORT))
    await site.start()

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)  # Создаем логгер для использования в других частях программы
    asyncio.run(main())