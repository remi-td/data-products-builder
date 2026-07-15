from sqlalchemy import text
from sqlalchemy.orm import Session

PING = text("SELECT 1 AS ok")


def ping(db: Session) -> bool:
    row = db.execute(PING).first()
    return bool(row and row[0] == 1)
