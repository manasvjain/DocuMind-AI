from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Building, Parcel, Project, Road, User, Vegetation, WaterBody, Role

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])


def _feature_rows(db: Session, ids: set[str]):
    if not ids:
        return []
    rows = []
    for model, kind in ((Building, "building"), (Road, "road"), (WaterBody, "water"), (Vegetation, "vegetation"), (Parcel, "parcel")):
        for row in db.scalars(select(model).where(model.project_id.in_(ids))):
            confidence = float(getattr(row, "confidence", getattr(row, "boundary_confidence", 0.0)))
            rows.append((kind, confidence))
    return rows


@router.get("/summary")
def summary(project_id: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    visible_projects = list(db.scalars(select(Project))) if user.role == Role.ADMIN else list(db.scalars(select(Project).where(Project.owner_id == user.id)))
    ids = {p.id for p in visible_projects}
    if project_id:
        ids = {project_id} if project_id in ids else set()

    def count_sum(model, field: str | None = None):
        if not ids:
            return 0
        query = select(func.count(model.id)) if field is None else select(func.coalesce(func.sum(getattr(model, field)), 0))
        return db.scalar(query.where(model.project_id.in_(ids))) or 0

    roofs = Counter()
    for b in db.scalars(select(Building).where(Building.project_id.in_(ids) if ids else False)):
        roofs[b.roof_type or "Unknown"] += 1

    rows = _feature_rows(db, ids)
    feature_distribution = Counter(kind for kind, _ in rows)
    confidence_distribution = Counter()
    for _, confidence in rows:
        bucket = min(0.95, max(0.5, int(confidence * 10) / 10))
        confidence_distribution[f"{bucket:.1f}-{bucket + 0.1:.1f}"] += 1

    area_buckets = Counter()
    for area in db.scalars(select(Building.area_m2).where(Building.project_id.in_(ids) if ids else False)):
        value = float(area or 0)
        if value < 50: label = "<50 m²"
        elif value < 100: label = "50-100 m²"
        elif value < 250: label = "100-250 m²"
        elif value < 500: label = "250-500 m²"
        else: label = "500+ m²"
        area_buckets[label] += 1

    return {
        "projects": len(ids),
        "processed_villages": sum(1 for p in visible_projects if p.id in ids and p.processing_status.startswith("COMPLETED")),
        "buildings": int(count_sum(Building)),
        "total_built_up_area_m2": float(count_sum(Building, "area_m2")),
        "road_length_m": float(count_sum(Road, "length_m")),
        "water_area_m2": float(count_sum(WaterBody, "area_m2")),
        "vegetation_area_m2": float(count_sum(Vegetation, "area_m2")),
        "parcels": int(count_sum(Parcel)),
        "roof_distribution": dict(roofs),
        "feature_distribution": dict(feature_distribution),
        "confidence_distribution": dict(sorted(confidence_distribution.items())),
        "building_area_distribution": dict(area_buckets),
        "village_statistics": [
            {"village": p.village_name, "status": p.processing_status, "model_version": p.model_version}
            for p in visible_projects if p.id in ids
        ],
    }
