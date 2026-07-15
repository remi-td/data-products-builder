import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.queries import overview as q
from app.schemas import Overview

router = APIRouter(prefix="/api/overview", tags=["overview"])
logger = logging.getLogger(__name__)


@router.get("", response_model=Overview)
def overview(db: Session = Depends(get_db)) -> Overview:
    try:
        return Overview(**q.fetch(db))
    except OperationalError:
        logger.exception("overview failed")
        raise HTTPException(status_code=503, detail="Database unavailable")
