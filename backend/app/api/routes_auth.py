from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user
from ..models.user import User
from ..schemas import (
    UserRegister,
    UserLogin,
    Token,
    TelegramAuth,
    UserRead,
)
from ..security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register_user(
    payload: UserRegister,
    db: Session = Depends(get_db),
):
    # Проверяем, есть ли уже такой email/phone
    if payload.email:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

    if payload.phone:
        existing = db.query(User).filter(User.phone == payload.phone).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this phone already exists",
            )

    user = User(
        role=payload.role,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2PasswordRequestForm:
    - username: можно передавать email или phone
    - password
    """
    login_value = form_data.username
    password = form_data.password

    user = (
        db.query(User)
        .filter((User.email == login_value) | (User.phone == login_value))
        .first()
    )

    if not user or not verify_password(password, user.password_hash or ""):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/telegram/login-or-register", response_model=Token)
def telegram_login_or_register(
    payload: TelegramAuth,
    db: Session = Depends(get_db),
):
    """
    Логика:
    1) Ищем по telegram_id — если есть, используем его
    2) Иначе, если есть phone — ищем по телефону и привязываем telegram_id
    3) Иначе — создаём нового пользователя с этим telegram_id
    """

    # 1. По telegram_id
    user = (
        db.query(User)
        .filter(User.telegram_id == payload.telegram_id)
        .first()
    )

    # 2. Если нет — по телефону
    if user is None and payload.phone:
        user = db.query(User).filter(User.phone == payload.phone).first()
        if user:
            user.telegram_id = payload.telegram_id
            db.add(user)
            db.commit()
            db.refresh(user)

    # 3. Если всё равно нет — создаём
    if user is None:
        user = User(
            role=payload.role or "tenant",
            name=payload.name or "Telegram User",
            phone=payload.phone,
            telegram_id=payload.telegram_id,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Выдаём токен
    access_token = create_access_token({"sub": str(user.id)})
    return Token(access_token=access_token)
