from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def kb_generation(kb_list) -> ReplyKeyboardBuilder:
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def spec_kb_generation(kb_list: str, next_button: bool = False, quick_replace: bool = False) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    if next_button: builder.add(KeyboardButton(text='Дальше'))
    for item in kb_list.split('='):
        builder.button(text='Дальше' if quick_replace and item=='Ребёнок не участвовал' else item)
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def rates_kb_generation(start: int, end: int) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    for i in range(start, end):
        builder.add(KeyboardButton(text=str(i)))
    builder.adjust(5)
    return builder.as_markup(resize_keyboard=True)