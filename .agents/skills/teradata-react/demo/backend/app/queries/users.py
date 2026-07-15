from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache import ttl_cached

LIST = text("""
    SELECT  TRIM(username)         AS username,
            createtimestamp,
            lastaltertimestamp,
            TRIM(creatorname)      AS ownername
    FROM    dbc.UsersV
    ORDER BY createtimestamp DESC NULLS LAST
""")


@ttl_cached(lambda db, limit=200: ("users", limit))
def list_recent(db: Session, limit: int = 200) -> list[dict]:
    rows = db.execute(LIST).mappings().fetchmany(limit)
    return [dict(r) for r in rows]
