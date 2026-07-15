from functools import lru_cache
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool
from app.settings import settings


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    # teradatasqlalchemy defaults to SingletonThreadPool; override with QueuePool so we
    # control the number of concurrent Teradata sessions (licensed resource).
    # pool_size + max_overflow = max simultaneous sessions — set with DBA awareness.
    return create_engine(
        settings.get_connection_url(),
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=1800,
        future=True,
    )
