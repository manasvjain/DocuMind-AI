from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models import Role,User
def ensure_admin(db:Session,email:str,password:str,full_name:str="System Administrator")->User:
    existing=db.scalar(select(User).where(User.email==email.lower()))
    if existing: return existing
    user=User(email=email.lower(),full_name=full_name,password_hash=hash_password(password),role=Role.ADMIN); db.add(user); db.commit(); db.refresh(user); return user
