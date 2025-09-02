from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.lexicon import lexicon_ru
from src.callbacks import callback_data

menu_btn = InlineKeyboardButton(text=lexicon_ru.MENU_BTN_TEXT,
                                callback_data=lexicon_ru.MENU_BTN_CALLBACK)


def gen_start_keyboard():
    builder = InlineKeyboardBuilder()
    for btn_text, btn_callback in lexicon_ru.START_KEYBOARD_DICT.items():
        builder.row(InlineKeyboardButton(text=btn_text,
                                         callback_data=btn_callback))
    return builder.as_markup()


def gen_coworking_keyboard():
    builder = InlineKeyboardBuilder()
    # Все остальные кнопки добавляются тут
    builder.row(menu_btn)
    return builder.as_markup()


def gen_nvk_links_keyboard():
    builder = InlineKeyboardBuilder()
    # Все остальные кнопки добавляются тут
    builder.row(menu_btn)
    return builder.as_markup()


def gen_check_in_keyboard():
    builder = InlineKeyboardBuilder()
    # Все остальные кнопки добавляются тут
    builder.row(menu_btn)
    return builder.as_markup()


def gen_report_keyboard():
    builder = InlineKeyboardBuilder()
    # Все остальные кнопки добавляются тут
    builder.row(menu_btn)
    return builder.as_markup()
