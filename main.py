from fastapi import FastAPI, Request
from database import Base, engine
app = FastAPI(docs_url='/')
# делаем миграции
Base.metadata.create_all(bind=engine)
# регистрируем компонент (роутер)
