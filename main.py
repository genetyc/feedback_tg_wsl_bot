import logging
import asyncio
from aiogram.types import BotCommand, BotCommandScopeDefault
from bot_create import bot, dp, ADMIN_ID, db, WEBHOOK_URL, API, REMOTE_PORT


async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def on_startup() -> None:
    # global file
    await set_commands()
    await bot.send_message(chat_id=ADMIN_ID, text='Бот запущен!')
    WEBHOOK_PATH = f"{WEBHOOK_URL}/{API}"
    await bot.set_webhook(WEBHOOK_PATH)
    # print("Bot is running...")
    await db.connect()        


from handlers import admin_panel, survey, mini_survey, start
async def on_shutdown() -> None:
    await bot.send_message(chat_id=ADMIN_ID, text='Бот остановлен!')
    await db.close()
    await bot.session.close()


async def main() -> None:
    dp.include_router(start.start_router)
    dp.include_router(survey.survey_router)
    dp.include_router(mini_survey.mini_survey_router)
    dp.include_router(admin_panel.admin_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    logging.basicConfig(level=logging.DEBUG)
    #await dp.start_polling(bot)
    await dp.start_webhook(
        webhook_path=f'/{API}',
        skip_updates=True,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host="0.0.0.0",
        port=int(REMOTE_PORT)
    )


if __name__ == "__main__":
    #logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    #logger = logging.getLogger(__name__)  # Создаем логгер для использования в других частях программы
    asyncio.run(main())