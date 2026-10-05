from pathlib import Path
class GCSStorage:
    def __init__(self,bucket_name:str):
        try: from google.cloud import storage
        except ImportError as exc: raise RuntimeError("google-cloud-storage is required for GCS mode") from exc
        self.client=storage.Client(); self.bucket=self.client.bucket(bucket_name)
    def upload_file(self,source:Path,key:str)->str:
        self.bucket.blob(key).upload_from_filename(str(source)); return key
    def download_file(self,key:str,destination:Path)->Path:
        destination.parent.mkdir(parents=True,exist_ok=True); self.bucket.blob(key).download_to_filename(str(destination)); return destination
    def delete(self,key:str)->None: self.bucket.blob(key).delete()
