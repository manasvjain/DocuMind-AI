import sys,uuid; sys.path.insert(0,'backend')
from fastapi.testclient import TestClient
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models import Project,Role,User
def test_parcel_confidence_filter_does_not_error():
    db=SessionLocal(); email=f"test-{uuid.uuid4().hex}@example.com"; password=uuid.uuid4().hex+"A!1"
    user=User(email=email,full_name="Test User",password_hash=hash_password(password),role=Role.ADMIN); db.add(user); db.commit(); db.refresh(user)
    project=Project(owner_id=user.id,village_name="Filter Test Village",district="Test",state="Test"); db.add(project); db.commit(); db.refresh(project); pid=project.id; uid=user.id; db.close()
    try:
        client=TestClient(app); login=client.post('/api/v1/auth/login',json={'email':email,'password':password}); assert login.status_code==200; client.headers.update({'Authorization':f"Bearer {login.json()['access_token']}"})
        response=client.get('/api/v1/features/parcel',params={'project_id':pid,'confidence':0.5}); assert response.status_code==200 and response.json()['count']==0
    finally:
        db=SessionLocal(); project=db.get(Project,pid)
        if project: db.delete(project)
        target=db.get(User,uid)
        if target: db.delete(target)
        db.commit(); db.close()
