from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.callbacks.callback_data import FAQCallback
from src.lexicon import lexicon_ru
from src.callbacks import callback_data

menu_btn = InlineKeyboardButton(text=lexicon_ru.MENU_BTN_TEXT,
                                callback_data=lexicon_ru.MENU_BTN_CALLBACK)

menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[[menu_btn]])


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


def gen_faq_keyboard():
    builder = InlineKeyboardBuilder()
    for btn_text, btn_callback in lexicon_ru.FAQ_BTN_DICT.items():
        builder.row(InlineKeyboardButton(text=btn_text,
                                         callback_data=FAQCallback(faq=btn_callback).pack()))
    builder.row(menu_btn)
    return builder.as_markup()


def gen_faq_keyboard_2(first_callback: str):
    chosen_dict = lexicon_ru.SERVICE_FAQ_DICT.get(first_callback)
    builder = InlineKeyboardBuilder()
    for btn_text, btn_callback in chosen_dict.items():
        builder.row(InlineKeyboardButton(text=btn_text,
                                         callback_data=btn_callback))
    builder.row(menu_btn)
    return builder.as_markup()
