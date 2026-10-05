from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import select
from app.core.config import get_settings
from app.models import Building,Road,WaterBody,Vegetation,Parcel,Project
def generate_report(db,project_id):
    p=db.get(Project,project_id)
    if not p: raise ValueError("Project not found")
    counts={}
    for model,name in ((Building,"Buildings"),(Road,"Roads"),(WaterBody,"Water bodies"),(Vegetation,"Vegetation"),(Parcel,"Candidate parcels")): counts[name]=len(list(db.scalars(select(model).where(model.project_id==project_id))))
    out=get_settings().storage_root/"exports"/project_id; out.mkdir(parents=True,exist_ok=True); path=out/"svamitrai_report.pdf"; styles=getSampleStyleSheet()
    doc=SimpleDocTemplate(str(path),pagesize=A4); story=[Paragraph("SVAMITRAI — Village Analysis Report",styles["Title"]),Spacer(1,12),Paragraph(f"<b>Village:</b> {p.village_name}",styles["BodyText"]),Paragraph(f"<b>Status:</b> {p.processing_status}",styles["BodyText"]),Spacer(1,12)]
    data=[["Feature","Count"]]+[[k,v] for k,v in counts.items()]; t=Table(data); t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("GRID",(0,0),(-1,-1),.5,colors.grey),("PADDING",(0,0),(-1,-1),6)])); story += [t,Spacer(1,16),Paragraph("Warning: AI-generated parcel boundaries are analytical outputs and must be validated against authoritative cadastral/survey records before legal use.",styles["BodyText"])]
    doc.build(story); return path
