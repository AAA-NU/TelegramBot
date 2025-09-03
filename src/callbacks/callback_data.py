from aiogram.filters.callback_data import CallbackData
# Пакет для работы с классами коллбек даты для фабрики коллбеков


# class ActionCallback(CallbackData, prefix='action'):
# action: str


class FAQCallback(CallbackData, prefix="faq"):
    faq: str

