from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import json


start_router = Router()

def load_messages():
    with open('/home/geneticisst/feedback_tg_wsl_bot/messages.json', 'r', encoding='utf-8') as file:
        return json.load(file)


msgs = load_messages()


@start_router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer(f"{msgs['start']}")


@start_router.message()
async def echo_handler(message: Message) -> None:
    await message.answer(f'Повторяю: <b>{message.text}</b>')