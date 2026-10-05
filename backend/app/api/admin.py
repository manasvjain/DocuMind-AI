from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.db.session import get_db
from app.models import Role, User
from app.schemas.auth import UserResponse

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), user: User = Depends(require_roles(Role.ADMIN))):
    return list(db.scalars(select(User).order_by(User.created_at.desc())))


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, payload: dict, db: Session = Depends(get_db), user: User = Depends(require_roles(Role.ADMIN))):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    if "role" in payload:
        target.role = Role(payload["role"])
    if "is_active" in payload:
        target.is_active = bool(payload["is_active"])
    db.commit()
    db.refresh(target)
    return target
