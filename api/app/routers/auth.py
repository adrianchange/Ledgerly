from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token, get_current_user, get_user_by_email, hash_password
from app.config import Settings, get_settings
from app.database import get_db
from app.models import User
from app.schemas import LoginIn, TokenOut, UserCreate, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(
    body: UserCreate,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenOut:
    email = body.email.lower()
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(str(user.id), settings)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/login", response_model=TokenOut)
def login_json(
    body: LoginIn,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenOut:
    user = authenticate_user(db, body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token(str(user.id), settings)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.post("/token", response_model=TokenOut, include_in_schema=False)
def login_form(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> TokenOut:
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = create_access_token(str(user.id), settings)
    return TokenOut(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user
