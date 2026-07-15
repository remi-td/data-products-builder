from sqlalchemy import text
from sqlalchemy.orm import Session

from app.cache import ttl_cached

OVERVIEW = text("""
    SELECT
      (SELECT COUNT(*) FROM dbc.DatabasesV)                              AS database_count,
      (SELECT COUNT(*) FROM dbc.TablesV WHERE tablekind IN ('T','V','O')) AS table_count,
      (SELECT COUNT(*) FROM dbc.UsersV)                                  AS user_count,
      (SELECT COALESCE(SUM(currentperm), 0) FROM dbc.DiskSpaceV)         AS total_perm_bytes
""")


@ttl_cached(lambda db: ("overview",))
def fetch(db: Session) -> dict:
    row = db.execute(OVERVIEW).mappings().first()
    return dict(row) if row else {
        "database_count": 0, "table_count": 0,
        "user_count": 0, "total_perm_bytes": 0.0,
    }
