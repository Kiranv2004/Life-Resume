from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate):
    existing = User.objects(email=payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(email=payload.email, password_hash=get_password_hash(payload.password)).save()
    return UserOut(id=str(user.id), email=user.email)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    user = User.objects(email=payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return Token(access_token=token)
