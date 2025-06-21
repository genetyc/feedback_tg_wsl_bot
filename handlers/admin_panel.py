from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, KeyboardButton
from states import AdminPanel
from keyboards.kb_generator import kb_generation
from states import Survey
from bot_create import db, admins, bot
from filters.is_admin import is_admin


admin_router = Router()


@admin_router.message(AdminPanel.admin_panel)
async def state0(message: Message, state: FSMContext):
    text = message.text
    if text == 'Назад':
        kb_list = [
            [KeyboardButton(text='Пройти опрос')] # TODO еще кнопка 'Оценить качество обучения'
        ]
        if is_admin(message.from_user.id):
            kb_list.append([KeyboardButton(text='Админ-панель')])
        await message.answer('Главная панель', reply_markup=kb_generation(kb_list=kb_list))
        await state.set_state(Survey.init_state)
    elif text == 'Средний рейтинг':
        rating = await db.get_average_edu_rating()
        await message.answer(f'Всего рецендентов:\t{rating[1]}\nСредний рейтинг обучения:\t{rating[0]:.2f}')
    elif text == 'Отчистить данные':
        await message.answer(f'Какие данные Вы хотите удалить?', reply_markup=kb_generation(kb_list = [
                [KeyboardButton(text="Данные большого опроса")], [KeyboardButton(text="Данные мини-опроса")], 
                [KeyboardButton(text="Все")], [KeyboardButton(text='Назад')]] 
            ))
        await state.set_state(AdminPanel.clear_check)
        
        ...
    elif text == 'Скачать данные':
        await db.export_to_excel_and_send(bot, message.chat.id)


@admin_router.message(AdminPanel.clear_check)
async def state_clear_check(message: Message, state: FSMContext):
    text = message.text
    if text == "Данные большого опроса":
        case=1
    elif text == "Данные мини-опроса":
        case=2
    elif text == 'Все':
        case=3
    elif text == 'Назад':
        await state.set_state(AdminPanel.admin_panel)
        await message.answer(f'Админ-панель', reply_markup=kb_generation(kb_list = [
            [KeyboardButton(text='Скачать данные')],
            [KeyboardButton(text='Средний рейтинг')],
            [KeyboardButton(text='Отчистить данные')],
            [KeyboardButton(text='Назад')]
        ]))
    else:
        case = None
    await message.answer('Вы уверены, что хотите удалить накопленные данные?', reply_markup=kb_generation(kb_list=[
        [KeyboardButton(text='Да')], [KeyboardButton(text='Нет')]
    ]))
    await state.set_state(AdminPanel.clear_double_check)
    await state.update_data(case=case)


@admin_router.message(AdminPanel.clear_double_check)
async def state_clear_double_check(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    case = data['case']
    reply_markup = kb_generation(kb_list = [
            [KeyboardButton(text='Скачать данные')],
            [KeyboardButton(text='Средний рейтинг')],
            [KeyboardButton(text='Отчистить данные')],
            [KeyboardButton(text='Назад')]
        ])
    if text == "Да" and case is not None:
        await db.clear_table(exceptions=admins, case=case)
        await message.answer('Данные отчищены!', reply_markup=reply_markup)
    else:
        await message.answer('Данные не были отчищены по какой-то причине', reply_markup=reply_markup)
    await state.set_state(AdminPanel.admin_panel)
    