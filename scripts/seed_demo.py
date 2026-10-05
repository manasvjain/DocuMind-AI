import json,os,shutil,sys
from pathlib import Path
sys.path.insert(0,"backend")
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import Imagery,ModelVersion,Project
from app.services.admin import ensure_admin
from app.services.image_validation import inspect_raster

password=os.environ.get("DEMO_ADMIN_PASSWORD")
if not password:
    raise SystemExit("Set DEMO_ADMIN_PASSWORD before running seed_demo.py")
settings=get_settings();root=Path(__file__).resolve().parents[1];db=SessionLocal()
try:
    admin=ensure_admin(db,os.environ.get("DEMO_ADMIN_EMAIL","demo-admin@example.com"),password,"SVAMITRAI Demo Administrator")
    model=db.query(ModelVersion).filter_by(name="unet",version="demo-rule-based").first()
    if not model:
        model=ModelVersion(name="unet",version="demo-rule-based",architecture="U-Net compatible demo pipeline",training_dataset="Synthetic DEMO ONLY",classes=["background","building","road","water","vegetation","candidate parcel"],status="ACTIVE",is_demo=True)
        db.add(model);db.commit()
    project=db.query(Project).filter_by(village_name="SVAMITRAI Demo Village",owner_id=admin.id).first()
    if not project:
        project=Project(owner_id=admin.id,village_name="SVAMITRAI Demo Village",district="Demo District",state="Madhya Pradesh",country="India",latitude=22.65,longitude=75.80,crs="EPSG:32643",description="Synthetic demo project; not survey data.")
        db.add(project);db.commit();db.refresh(project)
    src=root/"data/demo/demo_village_orthophoto.tif"
    if src.exists():
        key=f"demo/{project.id}/demo_village_orthophoto.tif";dst=settings.storage_root/key;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        if not db.query(Imagery).filter_by(project_id=project.id).first():
            db.add(Imagery(project_id=project.id,original_name=src.name,storage_key=key,mime_type="image/tiff",size_bytes=dst.stat().st_size,is_demo=True,**inspect_raster(dst)));db.commit()
    print(json.dumps({"admin_email":admin.email,"project_id":project.id,"demo":True},indent=2))
finally:
    db.close()
