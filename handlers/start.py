from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton
from aiogram.fsm.context import FSMContext
from states import Survey, MiniSurvey
from handlers.json_handler import msgs
from keyboards.kb_generator import kb_generation


start_router = Router()


# @start_router.message(CommandStart())   # TODO сделать что-то с сохранением прогресса
# async def command_start(message: Message, state: FSMContext) -> None:
#     await message.answer(f"{msgs['start']}")
#     await state.set_state(Survey.question1)
#     await message.answer(f"{msgs['did_receive_parents_report']}", reply_markup=kb_generation(kb_list = [
#         [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
#     ]))

@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await message.answer(f"{msgs['init']}", reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text='Оценить качество обучения'), KeyboardButton(text='Пройти опрос')]
    ]))
    await state.set_state(Survey.init_state)


@start_router.message(Survey.init_state)
async def init_def(message: Message, state: FSMContext) -> None:
    text = message.text
    if text == 'Оценить качество обучения':
        await state.set_state(MiniSurvey.question0)
        await message.answer(f"{msgs['anon']}", reply_markup=kb_generation(kb_list = [
            [KeyboardButton(text="Хочу пройти опрос анонимно"),
             KeyboardButton(text="Хочу оставить свои контакты")]
        ]))
    elif text == 'Пройти опрос':
        await state.set_state(Survey.question1)
        await message.answer(f"{msgs['did_receive_parents_report']}", reply_markup=kb_generation(kb_list = [
            [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
        ]))