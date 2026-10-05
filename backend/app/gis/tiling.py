from dataclasses import dataclass
from pathlib import Path
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

def write_tile(src:rasterio.DatasetReader,tile:Tile,output_dir:Path,prefix:str)->Path:
    output_dir.mkdir(parents=True,exist_ok=True); path=output_dir/f"{prefix}_r{tile.row:04d}_c{tile.col:04d}.tif"
    profile=src.profile.copy(); profile.update(width=int(tile.window.width),height=int(tile.window.height),transform=rasterio.windows.transform(tile.window,src.transform),tiled=True)
    with rasterio.open(path,"w",**profile) as dst: dst.write(src.read(window=tile.window))
    return path
