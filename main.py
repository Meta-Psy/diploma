from fastapi import FastAPI, HTTPException, Depends, Form, Cookie, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import bcrypt

from config import algorithm, secret_key, access_token_exp_minutes
from database import get_db
from database.models import Admin, User
from logging_config import logger
from api.user_api.user import user_router
from api.admin_api.admin import admin_router
from api.test_api.test import test_router

app = FastAPI(docs_url="/")
app.include_router(admin_router)
app.include_router(test_router)
app.include_router(user_router)

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    number: Optional[str] = None


class UserAuth(BaseModel):
    number: str
    # Для ответа не стоит возвращать пароль


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_user(db: Session, number: str):
    return db.query(User).filter(User.number == number).first()


def get_admin(db: Session, number: str):
    logger.info('')
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


def authenticate_user(db: Session, number: str, password: str):
    user = get_user(db, number)
    if user and verify_password(password, user.password):
        return user
    return None


def authenticate_admin(db: Session, number: str, password: str):
    admin = get_admin(db, number)
    if admin and verify_password(password, admin.password):
        return admin
    return None


oauth_schema = OAuth2PasswordBearer(tokenUrl="/token/user")


@app.post("/token/user", response_model=Token)
async def user_login(form: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    user = authenticate_user(db, form.username, form.password)
    if not user:
        logger.info(f"Не найден пользователь или неверный пароль для {form.username}")
        raise HTTPException(status_code=404, detail="Неправильный пароль или username")
    access_token_exp = timedelta(minutes=access_token_exp_minutes)
    access_token = create_access_token(data={"sub": user.number}, expire_date=access_token_exp)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/token/admin", response_model=Token)
async def admin_login(form: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    admin = authenticate_admin(db, form.username, form.password)
    if not admin:
        logger.info(f"Не найден администратор или неверный пароль для {form.username}")
        raise HTTPException(status_code=404, detail="Неправильный пароль или username")
    access_token_exp = timedelta(minutes=access_token_exp_minutes)
    access_token = create_access_token(data={"sub": admin.number}, expire_date=access_token_exp)
    return {"access_token": access_token, "token_type": "bearer"}


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
    return UserAuth(number=current_user.number)


@app.get("/admin/me", response_model=UserAuth)
async def admin_me(current_admin: Admin = Depends(get_current_admin)):
    return UserAuth(number=current_admin.number)


async def get_current_user_from_cookie(
        access_token: str = Cookie(None),
        db: Session = Depends(get_db)
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неавторизованный пользователь"
        )
    # Если токен начинается с "Bearer ", удаляем префикс
    if access_token.startswith("Bearer "):
        access_token = access_token[len("Bearer "):]
    try:
        payload = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        login = payload.get("sub")
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные данные токена"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )
    with get_db() as db_session:
        user = get_user(db_session, login)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        return user


async def get_current_admin_from_cookie(
        access_token: str = Cookie(None),
        db: Session = Depends(get_db)
):
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неавторизованный админ"
        )
    # Если токен начинается с "Bearer ", удаляем префикс
    if access_token.startswith("Bearer "):
        access_token = access_token[len("Bearer "):]
    try:
        payload = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        login = payload.get("sub")
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверные данные токена"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен"
        )
    with get_db() as db_session:
        admin = get_admin(db_session, login)
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        return admin


def get_user_by_login(db: Session, login: str) -> Optional[User]:
    return db.query(User).filter(User.number == login).first()


def get_admin_by_login(db: Session, login: str) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.number == login).first()


@app.get("/login/user", response_class=HTMLResponse)
async def login_form(request: Request):
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Login</title>
      </head>
      <body>
        <h2>Вход в систему</h2>
        <form action="/login" method="post">
          <label for="username">Логин (номер):</label>
          <input type="text" id="username" name="username" required>
          <br><br>
          <label for="password">Пароль:</label>
          <input type="password" id="password" name="password" required>
          <br><br>
          <button type="submit">Войти</button>
        </form>
      </body>
    </html>
    """


@app.get("/login/admin", response_class=HTMLResponse)
async def login_form(request: Request):
    return """
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Login</title>
      </head>
      <body>
        <h2>Вход в систему</h2>
        <form action="/login" method="post">
          <label for="username">Логин (номер):</label>
          <input type="text" id="username" name="username" required>
          <br><br>
          <label for="password">Пароль:</label>
          <input type="password" id="password" name="password" required>
          <br><br>
          <button type="submit">Войти</button>
        </form>
      </body>
    </html>
    """


@app.post("/login/user")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = get_user_by_login(db, login=username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")
    access_token_expires = timedelta(minutes=access_token_exp_minutes)
    token = create_access_token(data={"sub": user.number}, expire_date=access_token_expires)
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@app.post("/login/admin")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    admin = get_admin_by_login(db, login=username)
    if not admin or not verify_password(password, admin.password):
        raise HTTPException(status_code=400, detail="Неверное имя админа или пароль")
    access_token_expires = timedelta(minutes=access_token_exp_minutes)
    token = create_access_token(data={"sub": admin.number}, expire_date=access_token_expires)
    response = RedirectResponse(url="/home", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return response


@app.get("/home/user", response_class=HTMLResponse)
async def home(request: Request, current_user=Depends(get_current_user_from_cookie)):
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Home</title>
      </head>
      <body>
        <h2>Добро пожаловать, {current_user.first_name}!</h2>
        <p>Вы успешно вошли в систему.</p>
        <a href="/logout">Выйти</a>
      </body>
    </html>
    """


@app.get("/home/admin", response_class=HTMLResponse)
async def home(request: Request, current_user=Depends(get_current_admin_from_cookie)):
    return f"""
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Home</title>
      </head>
      <body>
        <h2>Добро пожаловать, {current_user.first_name}!</h2>
        <p>Вы успешно вошли в систему.</p>
        <a href="/logout">Выйти</a>
      </body>
    </html>
    """

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
