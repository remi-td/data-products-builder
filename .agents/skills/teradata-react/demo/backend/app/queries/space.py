from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache import ttl_cached

TOP_BY_PERM = text("""
    SELECT  TRIM(databasename) AS databasename,
            SUM(currentperm)   AS currentperm,
            SUM(maxperm)       AS maxperm
    FROM    dbc.DiskSpaceV
    GROUP BY 1
    ORDER BY currentperm DESC
""")


@ttl_cached(lambda db, limit=20: ("space.top", limit))
def top_by_perm(db: Session, limit: int = 20) -> list[dict]:
    rows = db.execute(TOP_BY_PERM).mappings().fetchmany(limit)
    return [dict(r) for r in rows]
