from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.backend.spaces_controller import CoworkingModel, RoomModel
from src.callbacks.callback_data import FAQCallback, CoworkingCallback, DateCallback, TimeCallback, RoomsCallback, \
    EndRoomCallback, GroupReportCallback, FAQCallback2
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


def gen_coworking_keyboard(coworkings: list[CoworkingModel]):
    builder = InlineKeyboardBuilder()
    for coworking_model in coworkings:
        builder.row(InlineKeyboardButton(text=f"Коворкинг номер {coworking_model.id}",
                                         callback_data=CoworkingCallback(id=coworking_model.id).pack()))
    builder.row(menu_btn)
    return builder.as_markup()


def gen_coworking_keyboard_2(dates: list[str]):
    builder = InlineKeyboardBuilder()
    for date in dates:
        builder.row(InlineKeyboardButton(text=date,
                                         callback_data=DateCallback(date=date).pack()))
    builder.row(menu_btn)
    return builder.as_markup()


def gen_coworking_keyboard_3(times: list[str]):
    builder = InlineKeyboardBuilder()
    for time in times:
        builder.row(InlineKeyboardButton(text=time,
                                         callback_data=TimeCallback(time=time.replace(":", ".")).pack()))
    builder.adjust(3)
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
                                         callback_data=FAQCallback2(faq=btn_callback).pack()))
    builder.row(menu_btn)
    return builder.as_markup()


def gen_start_admin_keyboard():
    builder = InlineKeyboardBuilder()
    for btn_text, btn_callback in lexicon_ru.START_ADMIN_KEYBOARD_DICT.items():
        builder.row(InlineKeyboardButton(text=btn_text,
                                         callback_data=btn_callback))
    return builder.as_markup()


def gen_rooms_keyboard(rooms: list[RoomModel]):
    builder = InlineKeyboardBuilder()
    for room_model in rooms:
        if not room_model.is_booked:
            builder.row(InlineKeyboardButton(text=f"Аудитория {room_model.id}",
                                             callback_data=RoomsCallback(room_id=room_model.id).pack()))
    builder.row(menu_btn)
    return builder.as_markup()


def gen_booking_end_keyboard(room_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Завершить бронирование",
                                     callback_data=EndRoomCallback(room_id=room_id).pack()))
    return builder.as_markup()


def gen_report_group_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=lexicon_ru.REPORT_GROUP_BTN,
                                     callback_data=GroupReportCallback(user_id=user_id).pack()))
    return builder.as_markup()
