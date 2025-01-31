from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
# указываем тип и название базы данных
SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
# создаём движок нашей базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URI)
# создание функции для создания сессий
SessionLocal = sessionmaker(bind=engine)
# создаём суперкласс для модели (будем его наследовать наподобие Models в django)
Base = declarative_base()
# создание функции генератора сессии


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()



