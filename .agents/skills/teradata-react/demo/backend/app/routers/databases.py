import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.queries import databases as q
from app.schemas import DatabaseRow

router = APIRouter(prefix="/api/databases", tags=["databases"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[DatabaseRow])
def list_databases(
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[DatabaseRow]:
    try:
        return [DatabaseRow(**r) for r in q.list_top(db, limit)]
    except OperationalError:
        logger.exception("list_databases failed")
        raise HTTPException(status_code=503, detail="Database unavailable")
