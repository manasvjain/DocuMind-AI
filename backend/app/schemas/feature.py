from pydantic import BaseModel
class FeatureProperties(BaseModel):
    id:str; feature_type:str; confidence:float; model_version:str|None=None; area_m2:float|None=None; perimeter_m:float|None=None; length_m:float|None=None; width_m:float|None=None; compactness:float|None=None; roof_type:str|None=None; roof_confidence:float|None=None; coverage_pct:float|None=None; is_authoritative:bool|None=None
class GeoJSONFeature(BaseModel): type:str="Feature"; geometry:dict; properties:dict
class FeatureCollection(BaseModel): type:str="FeatureCollection"; features:list[GeoJSONFeature]
