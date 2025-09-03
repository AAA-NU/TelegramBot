import asyncio

from aiogram import Router, Bot, F, BaseMiddleware
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, TelegramObject
from aiogram.types import ChatMemberUpdated, Chat, CallbackQuery
from aiogram.filters import ChatMemberUpdatedFilter, Command, StateFilter, CommandStart
from aiogram.enums import ChatMemberStatus, ChatType
from aiogram.filters.chat_member_updated import IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, default_state, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.token import TokenValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.callbacks.callback_data import FAQCallback, CoworkingCallback, DateCallback, TimeCallback
from src.keyboards import keyboards_ru
from src.lexicon import lexicon_ru
from src.states.bot_states import ReportStates
from typing import Callable, Dict, Awaitable, Any
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


class StudentAccessMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Получаем объект пользователя aiogram из данных события
        event_user = data.get('event_from_user')
        if not event_user:
            # Событие без пользователя (например, опрос в канале), пропускаем
            return await handler(event, data)

        # Запрашиваем пользователя из нашего API
        user_from_api = BackendUsersController.get_user_by_tg_id(event_user.id)

        # ГЛАВНАЯ ЛОГИКА ФИЛЬТРАЦИИ
        if user_from_api and user_from_api.role == 'student':
            # Если пользователь - студент, обогащаем данные и передаем управление дальше
            data['user'] = user_from_api
            return await handler(event, data)

        # Если пользователь не студент или не найден в API,
        # обработка на этом роутере прекращается.
        # Мы НЕ вызываем handler.
        # Опционально: можно ответить пользователю.
        if isinstance(event, Message):
            await event.answer("К сожалению, доступ к этому разделу есть только у студентов.")
        elif isinstance(event, CallbackQuery):
            await event.answer("Доступ запрещен", show_alert=True)

        # Так как мы не вызвали await handler(...), aiogram не будет
        # искать обработчики для этого события в данном роутере.
        return

from datetime import datetime, timedelta, date
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
router.message.middleware(StudentAccessMiddleware())
router.callback_query.middleware(StudentAccessMiddleware())


@router.callback_query(F.data == "coworking")
async def process_coworking_callback(callback: CallbackQuery):
    coworkings = SpacesApiController.get_coworkings()
    await callback.message.edit_text(text=lexicon_ru.COWORKING_TEXT,
                                     reply_markup=keyboards_ru.gen_coworking_keyboard(coworkings=coworkings))


@router.callback_query(F.data == "nvk_links")
async def process_nvk_links_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.NVK_LINKS_TEXT,
                                     reply_markup=keyboards_ru.gen_nvk_links_keyboard())


@router.callback_query(F.data == "check_in")
async def process_check_in_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.CHECK_IN_TEXT,
                                     reply_markup=keyboards_ru.gen_check_in_keyboard())


@router.callback_query(F.data == "report")
async def process_report_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReportStates.wait_message_with_photo)
    await callback.message.edit_text(text=lexicon_ru.REPORT_TEXT,
                                     reply_markup=keyboards_ru.gen_report_keyboard())


@router.message(F.photo, StateFilter(ReportStates.wait_message_with_photo))
async def process_report_photo(message: Message):
    await message.send_copy(chat_id=ADMIN_GROUP_ID) # Тут можно добавить функцию обработки(то есть админ нажимает, что репорт обработан и пользователю приходит уведомление.)
    await message.answer(text="Успешно, твоя заявка отправлена!", reply_markup=keyboards_ru.menu_keyboard)


@router.callback_query(F.data == "FAQ")
async def process_faq_callback(callback: CallbackQuery):
    await callback.message.edit_text(text=lexicon_ru.FAQ_TEXT,
                                     reply_markup=keyboards_ru.gen_faq_keyboard())


@router.callback_query(FAQCallback.filter())
async def process_faq_2_callback(callback: CallbackQuery, callback_data: FAQCallback):
    await callback.message.edit_text(text=lexicon_ru.FAQ_TEXT,
                                     reply_markup=keyboards_ru.gen_faq_keyboard_2(first_callback=callback_data.faq))


@router.callback_query(CoworkingCallback.filter())
async def process_coworking_callback_2(callback: CallbackQuery, callback_data: CoworkingCallback, state: FSMContext):
    await state.update_data(cowo_id=callback_data.id)
    await callback.message.edit_text(text=lexicon_ru.CHOICE_DATE_TEXT,
                                     reply_markup=keyboards_ru.gen_coworking_keyboard_2(dates=get_next_seven_days()))


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


@router.callback_query(TimeCallback.filter())
async def process_time_callback(callback: CallbackQuery, callback_data: TimeCallback, state: FSMContext):
    data = await state.get_data()
    cowo_id = data.get("cowo_id")
    cowo_date = data.get("cowo_date")
    cowo_time = callback_data.time.replace(".", ":")
    time_to_booking = f"{cowo_date} {cowo_time}"
    SpacesApiController.add_coworking_booking_time(coworking_id=cowo_id, time=time_to_booking)
    await callback.message.edit_text(text=lexicon_ru.SUCCESS_BOOKING,
                                     reply_markup=keyboards_ru.menu_keyboard)