from aiogram.filters.callback_data import CallbackData
# Пакет для работы с классами коллбек даты для фабрики коллбеков


# class ActionCallback(CallbackData, prefix='action'):
# action: str


class FAQCallback(CallbackData, prefix="faq"):
    faq: str


class CoworkingCallback(CallbackData, prefix="cowo"):
    id: str


class DateCallback(CallbackData, prefix="date"):
    date: str


class TimeCallback(CallbackData, prefix="time"):
    time: str


class RoomsCallback(CallbackData, prefix="rooms"):
    room_id: str


class EndRoomCallback(CallbackData, prefix="end_room"):
    room_id: str


class GroupReportCallback(CallbackData, prefix="group_report"):
    user_id: int
