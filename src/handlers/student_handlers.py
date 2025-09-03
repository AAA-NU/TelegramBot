from datetime import datetime, timedelta, date
import asyncio

from aiogram import Router, Bot, F, BaseMiddleware
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, TelegramObject
from aiogram.types import ChatMemberUpdated, Chat, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, StateFilter, CommandStart, BaseFilter, CommandObject
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters.chat_member_updated import IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.token import TokenValidationError
from requests import HTTPError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.backend.qr_controller import VerifyApiController
from src.callbacks.callback_data import FAQCallback, CoworkingCallback, DateCallback, TimeCallback, FAQCallback2
from src.keyboards import keyboards_ru
from src.lexicon import lexicon_ru
from src.states.bot_states import ReportStates
from typing import Callable, Dict, Awaitable, Any, Union
from src.backend.users_controller import BackendUsersController
from src.backend.spaces_controller import SpacesApiController

ADMIN_GROUP_ID = -4904031171


def get_next_seven_days():
    """
    Возвращает список из 7 строк с датами в формате 'ГГГГ-ММ-ДД',
    начиная с сегодняшнего дня.
    """
    # Создаем пустой список, куда будем добавлять даты
    date_list = []

    # Получаем сегодняшнюю дату
    today = date.today()

    # Запускаем цикл, который повторится 7 раз (для 7 дней)
    for i in range(7):
        # К сегодняшней дате прибавляем смещение в днях (от 0 до 6)
        # timedelta(days=i) создает объект "промежуток времени в i дней"
        current_date = today + timedelta(days=i)

        # Форматируем полученную дату в строку нужного формата 'ГГГГ-ММ-ДД'
        # %Y - год (4 цифры), %m - месяц (2 цифры), %d - день (2 цифры)
        formatted_date = current_date.strftime("%Y-%m-%d")

        # Добавляем отформатированную строку в наш список
        date_list.append(formatted_date)

    # Возвращаем готовый список
    return date_list


class RoleFilter(BaseFilter):
    def __init__(self, allowed_role: str):
        self.allowed_role = allowed_role

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        # Проверяем, есть ли вообще пользователь в событии
        if not event.from_user:
            return False
        try:
            # Делаем запрос в наше API прямо внутри фильтра
            user_from_api = BackendUsersController.get_user_by_tg_id(
                str(event.from_user.id))
        except HTTPError:
            return False
        # Если пользователь найден и его роль совпадает с разрешенной - фильтр пройден
        if user_from_api and user_from_api.role == self.allowed_role:
            return True

        # Во всех остальных случаях - не пропускаем
        return False


def string_to_date_strptime(date_string: str) -> date:
    """
    Преобразует строку с датой в формате 'ГГГГ-ММ-ДД'
    в объект datetime.date, используя strptime.

    Аргументы:
        date_string: Строка с датой (например, '2023-10-27').

    Возвращает:
        Объект datetime.date.
    """
    # %Y, %m, %d должны точно соответствовать формату строки
    format_code = "%Y-%m-%d"

    # datetime.strptime создает объект datetime (с временем 00:00:00)
    datetime_object = datetime.strptime(date_string, format_code)

    # Возвращаем из него только часть с датой
    return datetime_object.date()


router = Router()
router.message.filter(RoleFilter("student"))
router.callback_query.filter(RoleFilter("student"))


@router.message(CommandStart(deep_link=True, magic=F.args))
async def process_start_with_deeplink(message: Message, command: CommandObject):
    deeplink_param = command.args
    verify_result = VerifyApiController.verify_uuid(uuid=deeplink_param)
    if verify_result.valid:
        await message.answer(text=lexicon_ru.SUCCESS_CHECK_IN)
    else:
        await message.answer(text=lexicon_ru.UNSUCCESS_CHECK_IN)


@router.message(CommandStart())
async def show_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=lexicon_ru.START_MESSAGE_TEXT,
                         reply_markup=keyboards_ru.gen_start_keyboard())


@router.callback_query(F.data == "coworking")
async def process_coworking_callback(callback: CallbackQuery):
    coworkings = SpacesApiController.get_coworkings()
    await callback.message.edit_text(text=lexicon_ru.COWORKING_TEXT,
                                     reply_markup=keyboards_ru.gen_coworking_keyboard(coworkings=coworkings))
    await callback.answer()


@router.callback_query(F.data == "nvk_links")
async def process_nvk_links_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.NVK_LINKS_TEXT,
                                     reply_markup=keyboards_ru.gen_nvk_links_keyboard())
    await callback.answer()


@router.callback_query(F.data == "check_in")
async def process_check_in_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.CHECK_IN_TEXT,
                                     reply_markup=keyboards_ru.gen_check_in_keyboard())
    await callback.answer()


@router.callback_query(F.data == "report")
async def process_report_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReportStates.wait_message_with_photo)
    await callback.message.edit_text(text=lexicon_ru.REPORT_TEXT,
                                     reply_markup=keyboards_ru.gen_report_keyboard())
    await callback.answer()


@router.message(F.photo, StateFilter(ReportStates.wait_message_with_photo))
async def process_report_photo(message: Message, bot: Bot):
    # Тут можно добавить функцию обработки(то есть админ нажимает, что репорт обработан и пользователю приходит уведомление.)
    await message.send_copy(chat_id=ADMIN_GROUP_ID)
    await bot.send_message(chat_id=ADMIN_GROUP_ID, text=lexicon_ru.REPORT_GROUP_TEXT,
                           reply_markup=keyboards_ru.gen_report_group_keyboard(user_id=message.from_user.id))
    await message.answer(text="Успешно, твоя заявка отправлена!", reply_markup=keyboards_ru.menu_keyboard)


@router.callback_query(F.data == "FAQ")
async def process_faq_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.FAQ_TEXT,
                                     reply_markup=keyboards_ru.gen_faq_keyboard())
    await callback.answer()


@router.callback_query(FAQCallback.filter())
async def process_faq_2_callback(callback: CallbackQuery, callback_data: FAQCallback):
    await callback.message.edit_text(text=lexicon_ru.FAQ_TEXT,
                                     reply_markup=keyboards_ru.gen_faq_keyboard_2(first_callback=callback_data.faq))
    await callback.answer()


@router.callback_query(FAQCallback2.filter())
async def process_faq_3_callback(callback: CallbackQuery, callback_data: FAQCallback2):
    ans = lexicon_ru.SERVICE_FAQ_DICT_2.get(callback_data.faq)
    if not ans:
        ans = lexicon_ru.NEXT_TIME_ANSWER_TEXT
    await callback.message.edit_text(text=ans, reply_markup=keyboards_ru.menu_keyboard)
    ans


@router.callback_query(CoworkingCallback.filter())
async def process_coworking_callback_2(callback: CallbackQuery, callback_data: CoworkingCallback, state: FSMContext):
    await state.update_data(cowo_id=callback_data.id)
    await callback.message.edit_text(text=lexicon_ru.CHOICE_DATE_TEXT,
                                     reply_markup=keyboards_ru.gen_coworking_keyboard_2(dates=get_next_seven_days()))
    await callback.answer()


@router.callback_query(DateCallback.filter())
async def process_date_callback(callback: CallbackQuery, callback_data: DateCallback, state: FSMContext):
    data = await state.get_data()
    cowo_id = data.get("cowo_id")
    cowo_date = callback_data.date
    await state.update_data(cowo_date=cowo_date)
    coworking_response = SpacesApiController.get_coworking_available_time(coworking_id=cowo_id,
                                                                          date_param=string_to_date_strptime(date_string=cowo_date))
    await callback.message.edit_text(text=lexicon_ru.CHOICE_TIME_TEXT,
                                     reply_markup=keyboards_ru.gen_coworking_keyboard_3(times=coworking_response.available_times))
    await callback.answer()


@router.callback_query(TimeCallback.filter())
async def process_time_callback(callback: CallbackQuery, callback_data: TimeCallback, state: FSMContext):
    data = await state.get_data()
    cowo_id = data.get("cowo_id")
    cowo_date = data.get("cowo_date")
    cowo_time = callback_data.time.replace(".", ":")
    time_to_booking = f"{cowo_date} {cowo_time}"
    SpacesApiController.add_coworking_booking_time(
        coworking_id=cowo_id, time=time_to_booking)
    await callback.message.edit_text(text=lexicon_ru.SUCCESS_BOOKING.format(cw_id=cowo_id, time=time_to_booking),
                                     reply_markup=keyboards_ru.menu_keyboard)
    await callback.answer()
