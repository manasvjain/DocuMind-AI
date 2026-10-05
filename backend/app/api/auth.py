from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.security import create_access_token, create_refresh_token, decode_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User, Role
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name.strip(), password_hash=hash_password(payload.password), role=Role.VIEWER)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id, user.role.value), refresh_token=create_refresh_token(user.id))


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    try:
        token = decode_token(payload.refresh_token)
        if token.get("type") != "refresh":
            raise ValueError
        user = db.get(User, token["sub"])
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token") from exc
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or missing")
    return TokenResponse(access_token=create_access_token(user.id, user.role.value), refresh_token=create_refresh_token(user.id))


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(current_user)):
    return user


@router.post("/logout")
def logout():
    return {"message": "Logged out. Discard the client token; refresh-token revocation can be added with a persistent token blacklist for stricter deployments."}
