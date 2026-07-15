import logging
from fastapi import APIRouter, Depends
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.queries import health as q
from app.schemas import HealthResponse

router = APIRouter(prefix="/api/health", tags=["health"])
logger = logging.getLogger(__name__)


@router.get("", response_model=HealthResponse)
def healthcheck(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        ok = q.ping(db)
        return HealthResponse(status="ok" if ok else "degraded", database="up")
    except OperationalError:
        logger.exception("healthcheck failed")
        return HealthResponse(status="degraded", database="down")
