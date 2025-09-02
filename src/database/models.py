from sqlalchemy.orm import relationship

from src.database.database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, BigInteger, DateTime, func
from sqlalchemy import Enum as SQLEnum
from enum import Enum
from datetime import datetime, timedelta


class SubscriptionType(str, Enum):
    FREE = "Бесплатный"
    TRIAL = "Пробный"
    STANDARD = "Стандартный"
    PREMIUM = "Премиум"


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=False)

    username = Column(String, nullable=False)

    first_name = Column(String, nullable=False)



