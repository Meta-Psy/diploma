from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from config import algorithm, secret_key, access_token_exp_minutes
from datetime import datetime, timedelta
from jose import jwt

app = FastAPI(docs_url="/")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str


class User(BaseModel):
    username: str
    password: str


fake_db = {
    "jonhdoe": {
        "username": "jonhdoe",
        "password": "123"
    }
}


# Функия для проверки пароля
def verify_password(password, hashed_password):
    return password == hashed_password


# Функция для получения пользователя
def get_user(db, username):
    if username in db:
        user_dict = db[username]
        return User(**user_dict)


# Функция для создания токена доступа
def create_access_token(data: dict, expire_date: Optional[timedelta] = None):
    # Копируем данные
    to_encode = data.copy()
    if expire_date:
        expire = datetime.utcnow() + expire_date
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    # Обновляем наши данные
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)

    return encoded_jwt


# Функция для авторизации
def authenticate_user(db, username: str, password: str):
    user = get_user(db, username)  # User(username=johndoe, password=123)
    if user and verify_password(password, user.password):
        return user
    return False


from fastapi import HTTPException, Depends


@app.post("/token", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_db, form.username, form.password)
    if not user:
        return HTTPException(status_code=404,
                             detail="Неправильный пароль или username")
    access_token_axpire = timedelta(minutes=access_token_exp_minutes)
    access_token = create_access_token(data={"sub": user.username},
                                       expire_date=access_token_axpire)
    return {"access_token": access_token,
            "token_type": "bearer"}


oauth_schema = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth_schema)):
    exeption = HTTPException(status_code=404,
                             detail="ERROR")
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise exeption
        # token_data = TokenData(username)
    except jwt.JWTError:
        raise exeption
    user = get_user(fake_db, username)
    if user is None:
        raise exeption
    return user


@app.get("/user/me", response_model=User)
async def user_me(user: User = Depends(get_current_user)):
    return user