def safe_geojson_geometry(value):
    if value is None: return None
    if hasattr(value, "__geo_interface__"): return value.__geo_interface__
    return value
