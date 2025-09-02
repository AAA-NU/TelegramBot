from aiogram.fsm.state import StatesGroup, State

# 1)токен бота
# 2)канал
# 3)способ оплаты(пока что 1)
# 4)сумма оплаты
# 5)длительность подписки(дней)


class BotRegistration(StatesGroup):
    wait_api_token = State()
    wait_channel = State()
    wait_payment_method = State()
    wait_amount = State()
    wait_subscribe_time = State()


