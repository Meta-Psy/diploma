from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from jose.exceptions import JWTError
from config import algorithm, secret_key, access_token_exp_minutes
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from database import get_db
from database.models import Admin, User
from logging_config import logger
import bcrypt
from api.user_api.user import user_router
from api.admin_api.admin import admin_router
from api.test_api.test import test_router

app = FastAPI(docs_url="/")
app.include_router(admin_router)
app.include_router(user_router)
app.include_router(test_router)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    number: Optional[str] = None


class UserAuth(BaseModel):
    number: str
    password: str


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_user(db, number: str):
    return db.query(User).filter(User.number == number).first()


def get_admin(db, number: str):
    return db.query(Admin).filter(Admin.number == number).first()


def create_access_token(data: dict, expire_date: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_date:
        expire = datetime.utcnow() + expire_date
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def authenticate_user(db, number: str, password: str):
    user = get_user(db, number)
    if user and verify_password(password, user.password):
        return user
    return None


def authenticate_admin(db, number: str, password: str):
    admin = get_admin(db, number)
    if admin and verify_password(password, admin.password):
        return admin
    return None


@app.post("/token/user", response_model=Token)
async def user_login(form: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    user = authenticate_user(db, form.username, form.password)
    if not user:
        logger.info(f"Не найден пользователь или неверный пароль для {form.username}")
        raise HTTPException(status_code=404, detail="Неправильный пароль или username")
    access_token_expire = timedelta(minutes=access_token_exp_minutes)
    access_token = create_access_token(data={"sub": user.number},
                                       expire_date=access_token_expire)
    logger.info(f"Пользователь {user.number} успешно авторизован")
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token/admin", response_model=Token)
async def admin_login(form: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    admin = authenticate_admin(db, form.username, form.password)
    if not admin:
        logger.info(f"Не найден пользователь или неверный пароль для {form.username}")
        raise HTTPException(status_code=404, detail="Неправильный пароль или username")
    access_token_expire = timedelta(minutes=access_token_exp_minutes)
    access_token = create_access_token(data={"sub": admin.number},
                                       expire_date=access_token_expire)
    logger.info(f"Пользователь {admin.number} успешно авторизован")
    return {"access_token": access_token, "token_type": "bearer"}

oauth_schema = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth_schema)):
    exception = HTTPException(status_code=404, detail="Ошибка авторизации")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        number: str = payload.get("sub")
        if number is None:
            raise exception
        token_data = TokenData(number=number)
    except JWTError:
        logger.error("Ошибка декодирования токена", exc_info=True)
        raise exception
    with get_db() as db:
        user = get_user(db, token_data.number)
        if user is None:
            raise exception
        return user


async def get_current_admin(token: str = Depends(oauth_schema)):
    exception = HTTPException(status_code=404, detail="Ошибка авторизации")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        number: str = payload.get("sub")
        if number is None:
            raise exception
        token_data = TokenData(number=number)
    except JWTError:
        logger.error("Ошибка декодирования токена", exc_info=True)
        raise exception
    with get_db() as db:
        admin = get_admin(db, token_data.number)
        if admin is None:
            raise exception
        return admin


@app.get("/user/me", response_model=UserAuth)
async def user_me(current_user: User = Depends(get_current_user)):
    return UserAuth(number=current_user.number, password="")


@app.get("/admin/me", response_model=UserAuth)
async def user_me(current_user: Admin = Depends(get_current_user)):
    return UserAuth(number=current_user.number, password="")
