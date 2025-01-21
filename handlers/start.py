from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message


router = Router()


@router.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer(f"Привет, <b>{message.from_user.full_name}</b>! Как дела?")


@router.message()
async def echo_handler(message: Message) -> None:
    await message.answer(f'Повторяю: <b>{message.text}</b>')