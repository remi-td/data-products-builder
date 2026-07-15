import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.queries import users as q
from app.schemas import UserRow

router = APIRouter(prefix="/api/users", tags=["users"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[UserRow])
def list_users(
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> list[UserRow]:
    try:
        return [UserRow(**r) for r in q.list_recent(db, limit)]
    except OperationalError:
        logger.exception("list_users failed")
        raise HTTPException(status_code=503, detail="Database unavailable")
