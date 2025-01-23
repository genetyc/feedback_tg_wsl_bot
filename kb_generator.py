from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def kb_generation(kb_list) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard


def spec_kb_generation(kb_list) -> ReplyKeyboardBuilder:
    builder = ReplyKeyboardBuilder()
    for item in str(kb_list).split('-'):
        builder.button(text=item)
    builder.adjust(1, 1, 1)
    return builder.as_markup(resize_keyboard=True)