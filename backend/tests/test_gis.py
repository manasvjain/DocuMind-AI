import sys; sys.path.insert(0,'backend'); sys.path.insert(0,'.')
import numpy as np
from rasterio.transform import from_origin
from app.gis.vectorize import polygonize_class
from app.gis.metrics import compactness
from gis.raster.tiling import iter_tiles
def test_tiling_covers_edges():
    tiles=list(iter_tiles(1000,700,512,64)); assert tiles; assert max(int(t.window.col_off+t.window.width) for t in tiles)==1000; assert max(int(t.window.row_off+t.window.height) for t in tiles)==700
def test_polygonization_and_metrics():
    mask=np.zeros((100,100),dtype=np.uint8); mask[10:40,20:50]=1; feats=polygonize_class(mask,1,from_origin(500000,4600000,1,1),'EPSG:32643',min_area_m2=1,simplify_m=0); assert len(feats)==1; assert feats[0]['area_m2']>500; assert 0<compactness(feats[0]['area_m2'],feats[0]['perimeter_m'])<=1
