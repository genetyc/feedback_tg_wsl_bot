from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def kb_generation(kb_list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def spec_kb_generation(kb_list: str, next_button: bool = False) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    for item in kb_list.split('='):
        builder.button(text=item)
    if next_button: builder.add(KeyboardButton(text='Дальше'))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


# def multiple_choice_kb_generation(kb_list: str) -> InlineKeyboardMarkup:
#     builder = InlineKeyboardBuilder()
#     for item in kb_list.split('-'):
#         button = InlineKeyboardButton(text=item)
#         if item == "Другое":
#             button.callback_data = 'else'
#         elif item == 'Дальше':
#             button.callback_data = 'next'
#         else:
#             pass
#         builder.add(button)
#     return builder.as_markup()


def multiple_choice_kb_generation(kb_list: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, item in enumerate(kb_list.split('-')):
        if item == 'Другое':
            builder.add(InlineKeyboardButton(text=item, callback_data='other'))
        else:
            builder.add(InlineKeyboardButton(text=item, callback_data=f'option{index}'))
    builder.adjust(1)
    builder.add(InlineKeyboardButton(text='Дальше', callback_data='next'))
    return builder.as_markup()