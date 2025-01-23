from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from states import Survey
from json_handler import msgs
from kb_generator import kb_generation


start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await message.answer(f"{msgs['start']}")
    await state.set_state(Survey.question1)
    await message.answer(f"{msgs['did_receive_parents_report']}", reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
    ]))