from datetime import datetime
from sqlalchemy import (Column, Integer, String, Boolean, ForeignKey, DateTime)
import enum
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base


class TestLevel(enum.Enum):
    LEVEL_1 = 'objects'
    LEVEL_2 = 'actions'
    LEVEL_3 = 'skills'


class TestType(enum.Enum):
    TYPE_1 = 'type1'
    TYPE_2 = 'type2'
    TYPE_3 = 'type3'


class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, autoincrement=True, primary_key=True)
    admin_first_name = Column(String)
    admin_last_name = Column(String)
    number = Column(String, unique=True)
    password = Column(String)
    reg_date = Column(DateTime, default=datetime.now())


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, autoincrement=True, primary_key=True)

    user_first_name = Column(String)
    user_last_name = Column(String)
    number = Column(String, unique=True)

    par_first_name = Column(String)
    par_last_name = Column(String, nullable=True)
    par_number = Column(String)

    birthday = Column(String, nullable=True)
    school_class = Column(Integer, nullable=True)
    university = Column(String, nullable=True)
    group_number = Column(String, nullable=True)

    password = Column(String, default='123')
    is_blocked = Column(Boolean, default=False)
    reg_date = Column(DateTime, default=datetime.now())

    answers = relationship(argument="UserAnswer", backref="user", lazy='subquery')
    ratings = relationship(argument="TestRating", backref="user", lazy='subquery')


class Test(Base):
    __tablename__ = 'tests'
    id = Column(Integer, autoincrement=True, primary_key=True)
    question = Column(String)
    var_1 = Column(String)
    var_2 = Column(String)
    var_3 = Column(String)
    var_4 = Column(String)

    correct_answer = Column(String)
    timer = Column(Integer, default=0)

    level = Column(SAEnum(TestLevel), default=TestLevel.LEVEL_1)
    test_type = Column(SAEnum(TestType), default=TestType.TYPE_1)


class UserAnswer(Base):
    __tablename__ = 'user_answers'
    id = Column(Integer, autoincrement=True, primary_key=True)
    user_response = Column(String, default=False)
    correctness = Column(Boolean, default=False)

    answered_at = Column(DateTime, default=datetime.now())
    attempt = Column(Integer, default=0)
    timer = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey('users.id'))

    test_id = Column(Integer, ForeignKey('tests.id'))
    test = relationship(argument='Test', lazy='subquery')
    rating_id = Column(Integer, ForeignKey('test_rating.id'))


class TestRating(Base):
    __tablename__ = 'test_rating'
    id = Column(Integer, autoincrement=True, primary_key=True)
    correct_all = Column(Integer, default=0)
    category_objects_type1 = Column(Integer, default=0)
    category_objects_type2 = Column(Integer, default=0)
    category_actions_type1 = Column(Integer, default=0)
    category_actions_type2 = Column(Integer, default=0)
    category_actions_type3 = Column(Integer, default=0)
    category_skills_type1 = Column(Integer, default=0)
    category_skills_type2 = Column(Integer, default=0)
    category_skills_type3 = Column(Integer, default=0)
    time = Column(String)

    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    user_id = Column(Integer, ForeignKey('users.id'))
    user_answers = relationship(argument='UserAnswer', lazy='subquery')
