from functools import lru_cache
from pathlib import Path
import secrets
from pydantic import Field
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    app_name:str=Field(default="SVAMITRAI AI Feature Extraction",alias="APP_NAME")
    environment:str=Field(default="development",alias="ENVIRONMENT")
    database_url:str=Field(default="sqlite:///./data/svamitva.db",alias="DATABASE_URL")
    jwt_secret:str=Field(default_factory=lambda:secrets.token_urlsafe(32),alias="JWT_SECRET")
    jwt_expire_minutes:int=Field(default=60,alias="JWT_EXPIRE_MINUTES")
    refresh_token_expire_days:int=Field(default=7,alias="REFRESH_TOKEN_EXPIRE_DAYS")
    cors_origins:str=Field(default="http://localhost:5173",alias="CORS_ORIGINS")
    storage_backend:str=Field(default="local",alias="STORAGE_BACKEND")
    local_storage_path:str=Field(default="./data/outputs",alias="LOCAL_STORAGE_PATH")
    gcs_bucket:str|None=Field(default=None,alias="GCS_BUCKET")
    google_cloud_project:str|None=Field(default=None,alias="GOOGLE_CLOUD_PROJECT")
    vertex_ai_region:str=Field(default="asia-south1",alias="VERTEX_AI_REGION")
    model_bucket:str|None=Field(default=None,alias="MODEL_BUCKET")
    redis_url:str|None=Field(default=None,alias="REDIS_URL")
    max_upload_size:int=Field(default=5*1024**3,alias="MAX_UPLOAD_SIZE")
    default_tile_size:int=Field(default=512,alias="DEFAULT_TILE_SIZE")
    default_tile_overlap:int=Field(default=64,alias="DEFAULT_TILE_OVERLAP")
    confidence_threshold:float=Field(default=0.5,alias="CONFIDENCE_THRESHOLD")
    demo_mode:bool=Field(default=True,alias="DEMO_MODE")
    model_config=SettingsConfigDict(env_file=".env",extra="ignore",populate_by_name=True)
    @property
    def origins(self)->list[str]: return [v.strip() for v in self.cors_origins.split(",") if v.strip()]
    @property
    def storage_root(self)->Path:
        path=Path(self.local_storage_path); path.mkdir(parents=True,exist_ok=True); return path
@lru_cache
def get_settings()->Settings: return Settings()
