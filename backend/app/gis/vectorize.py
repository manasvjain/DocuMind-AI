from __future__ import annotations
import cv2, numpy as np, rasterio
from rasterio.features import shapes
from shapely.geometry import shape,mapping
from shapely.ops import transform as shapely_transform
from shapely.validation import make_valid
from pyproj import CRS,Transformer
CLASS_NAMES={0:"background",1:"building",2:"road",3:"water",4:"vegetation",5:"parcel"}

def clean_mask(mask,class_id,min_component_px=32):
    binary=(mask==class_id).astype(np.uint8); kernel=np.ones((3,3),np.uint8)
    binary=cv2.morphologyEx(binary,cv2.MORPH_OPEN,kernel,iterations=1); binary=cv2.morphologyEx(binary,cv2.MORPH_CLOSE,kernel,iterations=2)
    n,labels,stats,_=cv2.connectedComponentsWithStats(binary,connectivity=8); cleaned=np.zeros_like(binary)
    for label in range(1,n):
        if stats[label,cv2.CC_STAT_AREA]>=min_component_px: cleaned[labels==label]=1
    return cleaned

def polygonize_class(mask,class_id,transform,crs,min_area_m2=1.0,simplify_m=0.15):
    cleaned=clean_mask(mask,class_id); src_crs=CRS.from_user_input(crs) if crs else None; results=[]
    for geom,value in shapes(cleaned,mask=cleaned.astype(bool),transform=transform):
        if int(value)!=1: continue
        polygon=make_valid(shape(geom))
        if polygon.is_empty: continue
        if simplify_m: polygon=polygon.simplify(simplify_m,preserve_topology=True)
        area_m2=polygon.area; perimeter_m=polygon.length
        if src_crs and src_crs.is_geographic:
            utm=_local_utm(src_crs,polygon.centroid.x,polygon.centroid.y); projected=shapely_transform(Transformer.from_crs(src_crs,utm,always_xy=True).transform,polygon); area_m2=projected.area; perimeter_m=projected.length
        if area_m2<min_area_m2: continue
        results.append({"geometry":mapping(polygon),"area_m2":float(area_m2),"perimeter_m":float(perimeter_m),"centroid":(polygon.centroid.x,polygon.centroid.y)})
    return results

def _local_utm(crs,x,y):
    zone=int((x+180)//6)+1; return CRS.from_epsg((32600 if y>=0 else 32700)+zone)
