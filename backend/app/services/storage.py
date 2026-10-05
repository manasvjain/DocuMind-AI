from pathlib import Path
import os,shutil
class Storage:
    def __init__(self):
        from app.core.config import get_settings
        s=get_settings(); self.root=s.storage_root
    def path(self,key):
        p=(self.root/key).resolve()
        if not str(p).startswith(str(self.root.resolve())): raise ValueError("Invalid storage path")
        return p
    async def save_upload(self,upload,key,max_size):
        dest=self.path(key); dest.parent.mkdir(parents=True,exist_ok=True); size=0
        with dest.open("wb") as f:
            while chunk:=await upload.read(1024*1024):
                size+=len(chunk)
                if size>max_size: f.close(); dest.unlink(missing_ok=True); raise ValueError("Uploaded file exceeds maximum size")
                f.write(chunk)
        return dest,size
    def open_path(self,key): return self.path(key)
    def delete(self,key): self.path(key).unlink(missing_ok=True)
