from sqlalchemy import text
from sqlalchemy.orm import Session

LIST_BY_DATABASE = text("""
    SELECT  TRIM(databasename) AS databasename,
            TRIM(tablename)    AS tablename,
            tablekind,
            createtimestamp
    FROM    dbc.TablesV
    WHERE   databasename = :db
    ORDER BY tablename
""")


def list_by_database(db: Session, database: str, limit: int = 500) -> list[dict]:
    rows = db.execute(LIST_BY_DATABASE, {"db": database}).mappings().fetchmany(limit)
    return [dict(r) for r in rows]
