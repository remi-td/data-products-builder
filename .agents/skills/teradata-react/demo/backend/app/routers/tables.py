import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.queries import tables as q
from app.schemas import TableRow

router = APIRouter(prefix="/api/tables", tags=["tables"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[TableRow])
def list_tables(
    database: str = Query(..., min_length=1, max_length=128),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> list[TableRow]:
    try:
        return [TableRow(**r) for r in q.list_by_database(db, database, limit)]
    except OperationalError:
        logger.exception("list_tables failed db=%s", database)
        raise HTTPException(status_code=503, detail="Database unavailable")
