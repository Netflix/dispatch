from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dispatch.database.core import get_db

from .models import RouteRequest, RouteResponse
from .service import get

router = APIRouter()


@router.post("", response_model=RouteResponse)
def route(*, db_session: Session = Depends(get_db), route_in: RouteRequest):
    """
    Determine the correct entities to dispatch.
    """
    return {"recommendation": get(db_session=db_session, route_in=route_in)}
