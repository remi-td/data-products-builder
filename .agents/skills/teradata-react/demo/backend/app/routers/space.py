import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.queries import space as q
from app.schemas import SpaceByDatabase

router = APIRouter(prefix="/api/space", tags=["space"])
logger = logging.getLogger(__name__)


@router.get("/by-database", response_model=list[SpaceByDatabase])
def space_by_database(
    limit: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[SpaceByDatabase]:
    try:
        return [SpaceByDatabase(**r) for r in q.top_by_perm(db, limit)]
    except OperationalError:
        logger.exception("space_by_database failed")
        raise HTTPException(status_code=503, detail="Database unavailable")
