from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.api.features import _check_project, _feature
from app.db.session import get_db
from app.models import Building, User

router = APIRouter(prefix="/api/v1/buildings", tags=["buildings"])


@router.get("")
def list_buildings(project_id: str, min_confidence: float | None = None, roof_type: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    stmt = select(Building).where(Building.project_id == project_id)
    if min_confidence is not None:
        stmt = stmt.where(Building.confidence >= min_confidence)
    if roof_type:
        stmt = stmt.where(Building.roof_type == roof_type)
    rows = list(db.scalars(stmt))
    return {"type": "FeatureCollection", "features": [_feature("building", r) for r in rows], "count": len(rows)}
