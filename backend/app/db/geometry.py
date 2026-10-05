import json
from typing import Any
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator
try:
    from geoalchemy2 import Geometry
except ImportError:
    Geometry = None

class SpatialGeometry(TypeDecorator):
    impl = JSON
    cache_ok = True
    def load_dialect_impl(self,dialect):
        if dialect.name=="postgresql" and Geometry is not None:
            return dialect.type_descriptor(Geometry(geometry_type="GEOMETRY",srid=4326,spatial_index=False))
        if dialect.name=="postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(JSON)
    def process_bind_param(self,value:Any,dialect):
        if value is None: return None
        if dialect.name=="postgresql" and Geometry is not None:
            if isinstance(value,dict):
                from geoalchemy2.shape import from_shape
                from shapely.geometry import shape
                return from_shape(shape(value),srid=4326)
        return value
    def process_result_value(self,value,dialect):
        if value is None: return None
        if dialect.name=="postgresql" and Geometry is not None and hasattr(value,"data"):
            try:
                from geoalchemy2.shape import to_shape
                return to_shape(value).__geo_interface__
            except Exception: return value
        if isinstance(value,str):
            try: return json.loads(value)
            except Exception: return value
        return value
