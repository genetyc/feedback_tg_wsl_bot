from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, KeyboardButton
from aiogram.fsm.context import FSMContext
from states import Survey, MiniSurvey, AdminPanel
from handlers.json_handler import msgs
from keyboards.kb_generator import kb_generation
from bot_create import db, admins


start_router = Router()


@start_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    kb_list = [
        [KeyboardButton(text='Оценить качество обучения'), KeyboardButton(text='Пройти опрос')]
    ]
    if message.from_user.id in admins:
        kb_list.append([KeyboardButton(text='Админ-панель')])
    await message.answer(f"{msgs['init']}", reply_markup=kb_generation(kb_list=kb_list))
    await state.set_state(Survey.init_state)
    await db.add_user(telegram_id=message.from_user.id, table='public.survey')
    await db.add_user(telegram_id=message.from_user.id, table='public.mini_survey')


@start_router.message(Survey.init_state)
async def init_def(message: Message, state: FSMContext) -> None:
    text = message.text
    tgid = message.from_user.id
    if text == 'Оценить качество обучения':
        check = await db.fetchval("SELECT is_complete FROM public.mini_survey WHERE telegram_id = $1", tgid)
        if check == False:
            await state.set_state(MiniSurvey.question0)
            await message.answer(f"{msgs['anon']}", reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Хочу пройти опрос анонимно"),
                KeyboardButton(text="Хочу оставить свои контакты")]
            ]))
        else:
            await message.answer(f'Вы уже прошли опрос. Хотите пройти снова?', reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Пройти заново"), KeyboardButton(text="Нет")]
            ]))
            await state.set_state(Survey.double_check_state)
            await state.update_data(pointer=0)
    elif text == 'Пройти опрос':
        check = await db.fetchval("SELECT is_complete FROM public.survey WHERE telegram_id = $1", tgid)
        if check == False:
            await state.set_state(Survey.question1)
            await message.answer(f"{msgs['did_get_parents_report']}", reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
            ]))
        else:
            await message.answer(f'Вы уже прошли опрос. Хотите пройти снова?', reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Пройти заново"), KeyboardButton(text="Нет")]
            ]))
            await state.set_state(Survey.double_check_state)
            await state.update_data(pointer=1)
    elif text == 'Админ-панель' and tgid in admins:
        await state.set_state(AdminPanel.admin_panel)
        await message.answer(f'Админ-панель', reply_markup=kb_generation(kb_list = [
            [KeyboardButton(text='Скачать данные')],
            [KeyboardButton(text='Средний рейтинг')],
            [KeyboardButton(text='Отчистить данные')],
            [KeyboardButton(text='Назад')]
        ]))


@start_router.message(Survey.double_check_state)
async def double_check_def(message: Message, state: FSMContext) -> None:
    text = message.text
    data = await state.get_data()
    pointer = data['pointer']
    if text == 'Пройти заново':
        if pointer == 1:    # указатель на таблицу в базе данных (1 - большой опрос, 0 - маленький опрос)
            await state.set_state(Survey.question1)
            await message.answer(f"{msgs['did_get_parents_report']}", reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
            ]))
            await db.del_user(telegram_id=message.from_user.id)
            await db.add_user(telegram_id=message.from_user.id, table='public.survey')
        else:
            await state.set_state(MiniSurvey.question0)
            await message.answer(f"{msgs['anon']}", reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Хочу пройти опрос анонимно"),
                KeyboardButton(text="Хочу оставить свои контакты")]
            ]))
            await db.del_user(telegram_id=message.from_user.id, minisurvey=True)
            await db.add_user(telegram_id=message.from_user.id, table='public.mini_survey')
    elif text == 'Нет':
        kb_list = [
            [KeyboardButton(text='Оценить качество обучения'), KeyboardButton(text='Пройти опрос')]
        ]
        if message.from_user.id in admins:
            kb_list.append([KeyboardButton(text='Админ-панель')])
        await message.answer('Главная панель', reply_markup=kb_generation(kb_list=kb_list))
        await state.set_state(Survey.init_state)
        