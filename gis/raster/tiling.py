from dataclasses import dataclass
from typing import Iterator
import rasterio
from rasterio.windows import Window
@dataclass(frozen=True)
class Tile:
    row:int
    col:int
    window:Window
def iter_tiles(width:int,height:int,tile_size:int=512,overlap:int=64)->Iterator[Tile]:
    if tile_size<=0 or overlap<0 or overlap>=tile_size: raise ValueError("tile_size must be > 0 and overlap must satisfy 0 <= overlap < tile_size")
    stride=tile_size-overlap; row_idx=0; y=0
    while y<height:
        col_idx=0; x=0; h=min(tile_size,height-y)
        while x<width:
            w=min(tile_size,width-x); yield Tile(row_idx,col_idx,Window(x,y,w,h)); x+=stride; col_idx+=1
        y+=stride; row_idx+=1
