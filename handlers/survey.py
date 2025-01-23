from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from states import Survey
from json_handler import msgs, answrs
from kb_generator import kb_generation, spec_kb_generation


survey_router = Router()


@survey_router.message(Survey.question1)
async def state1(message: Message, state: FSMContext):
    print(message.text)
    await state.set_state(Survey.question2)
    await message.answer(f"{msgs['where_you_found_out']}", reply_markup=kb_generation(kb_list = [
        [KeyboardButton(text=i) for i in str(answrs['where_you_found_out']).split('-')]
    ]))


@survey_router.message(Survey.question2)
async def state2(message: Message, state: FSMContext):
    print(message.text)
    await state.set_state(Survey.question3)
    await message.answer(f"{msgs['what_is_quality_edu']}", reply_markup=spec_kb_generation(kb_list = answrs['what_is_quality_edu']))