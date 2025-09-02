from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
import pathlib


CURRENT_DIR = pathlib.Path(__file__).parent

PROJECT_ROOT = CURRENT_DIR.parent.parent

DB_PATH = PROJECT_ROOT / "AdminBot.db"

DB_URL = f"sqlite+aiosqlite:///{DB_PATH}"

# DB_URL = 'postgresql+asyncpg://postgres:qwerty@localhost/Todo'


engine = create_async_engine(DB_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()
