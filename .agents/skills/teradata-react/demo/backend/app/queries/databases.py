from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache import ttl_cached

LIST = text("""
    SELECT  TRIM(databasename) AS databasename,
            TRIM(ownername)    AS ownername,
            permspace,
            spoolspace,
            tempspace
    FROM    dbc.DatabasesV
    ORDER BY permspace DESC
""")


@ttl_cached(lambda db, limit=200: ("databases", limit))
def list_top(db: Session, limit: int = 200) -> list[dict]:
    rows = db.execute(LIST).mappings().fetchmany(limit)
    return [dict(r) for r in rows]
