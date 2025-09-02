from typing import Type

from aiogram.types import Message, User
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import User

# Логика работы с базой данных
# Функции добавления данных о пользователе и их использовании

