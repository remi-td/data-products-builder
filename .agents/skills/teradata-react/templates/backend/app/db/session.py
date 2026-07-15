from collections.abc import Generator
from sqlalchemy.orm import Session, sessionmaker
from app.db.engine import get_engine

def get_db() -> Generator[Session, None, None]:
    # SessionLocal created here (not module-level) so get_engine() is called after .env is loaded
    SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False, future=True)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
