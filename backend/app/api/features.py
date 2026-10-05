from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from shapely.geometry import Point, shape
from shapely.ops import transform
from pyproj import CRS, Transformer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.db.session import get_db
from app.models import Building, Project, Prediction, Road, User, Vegetation, WaterBody, Parcel, Role

router = APIRouter(prefix="/api/v1/features", tags=["features"])


def _check_project(db: Session, project_id: str, user: User) -> Project:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    if user.role != Role.ADMIN and project.owner_id != user.id:
        raise HTTPException(403, "Project access denied")
    return project


def _feature(feature_type: str, obj: Any) -> dict:
    props = {"id": obj.id, "feature_type": feature_type, "confidence": float(getattr(obj, "confidence", getattr(obj, "boundary_confidence", 0.0))), "model_version": getattr(obj, "model_version", None)}
    for src, dest in (("area_m2", "area_m2"), ("perimeter_m", "perimeter_m"), ("length_m", "length_m"), ("width_m", "width_m"), ("compactness", "compactness"), ("roof_type", "roof_type"), ("roof_confidence", "roof_confidence"), ("coverage_pct", "coverage_pct"), ("boundary_confidence", "boundary_confidence"), ("is_authoritative", "is_authoritative")):
        if hasattr(obj, src): props[dest] = getattr(obj, src)
    geometry = obj.geometry
    if hasattr(geometry, "__geo_interface__"): geometry = geometry.__geo_interface__
    return {"type": "Feature", "geometry": geometry, "properties": props}


def _list(model, feature_type: str, project_id: str, db: Session, user: User, confidence: float | None, limit: int):
    _check_project(db, project_id, user)
    stmt = select(model).where(model.project_id == project_id).limit(limit)
    rows = list(db.scalars(stmt))
    if confidence is not None:
        rows = [r for r in rows if float(getattr(r, "confidence", getattr(r, "boundary_confidence", 0.0))) >= confidence]
    return {"type": "FeatureCollection", "features": [_feature(feature_type, row) for row in rows], "count": len(rows)}


@router.get("/geojson")
def all_features(project_id: str, confidence: float | None = Query(None, ge=0, le=1), limit: int = Query(5000, ge=1, le=20000), db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    collections = [
        _list(Building, "building", project_id, db, user, confidence, limit),
        _list(Road, "road", project_id, db, user, confidence, limit),
        _list(WaterBody, "water", project_id, db, user, confidence, limit),
        _list(Vegetation, "vegetation", project_id, db, user, confidence, limit),
        _list(Parcel, "parcel", project_id, db, user, confidence, limit),
    ]
    features = [f for col in collections for f in col["features"]]
    return {"type": "FeatureCollection", "features": features}


@router.get("/{feature_type}")
def feature_collection(feature_type: str, project_id: str, confidence: float | None = Query(None, ge=0, le=1), roof_type: str | None = None, min_area: float | None = Query(None, ge=0), model_version: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    mapping = {"building": (Building, "building"), "road": (Road, "road"), "water": (WaterBody, "water"), "vegetation": (Vegetation, "vegetation"), "parcel": (Parcel, "parcel")}
    if feature_type not in mapping: raise HTTPException(404, "Unsupported feature type")
    data = _list(*mapping[feature_type], project_id, db, user, confidence, 20000)
    if roof_type or min_area is not None or model_version:
        filtered = []
        for feature in data["features"]:
            p = feature["properties"]
            if roof_type and p.get("roof_type") != roof_type: continue
            if min_area is not None and float(p.get("area_m2") or 0) < min_area: continue
            if model_version and p.get("model_version") != model_version: continue
            filtered.append(feature)
        data["features"] = filtered; data["count"] = len(filtered)
    return data


@router.get("/spatial/query")
def spatial_query(project_id: str, lon: float, lat: float, radius_m: float = Query(100, gt=0, le=10000), db: Session = Depends(get_db), user: User = Depends(current_user)):
    _check_project(db, project_id, user)
    point = Point(lon, lat); results = []
    for model, feature_type in ((Building, "building"), (Road, "road"), (WaterBody, "water"), (Vegetation, "vegetation"), (Parcel, "parcel")):
        for row in db.scalars(select(model).where(model.project_id == project_id)):
            try:
                geom = shape(row.geometry); zone = int((lon + 180) // 6) + 1; epsg = (32600 if lat >= 0 else 32700) + zone
                to_utm = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(epsg), always_xy=True).transform
                point_m = transform(to_utm, point); geom_m = transform(to_utm, geom)
                if geom_m.distance(point_m) <= radius_m: results.append(_feature(feature_type, row))
            except Exception: continue
    return {"type": "FeatureCollection", "features": results}
