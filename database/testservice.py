from database import get_db
from database.models import Test, TestLevel, TestType, TestAttempt
import random
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from logging_config import logger


def add_test_db(question, var_1, var_2, var_3, var_4,
                correct_answer, timer, level, test_type):
    try:
        with next(get_db()) as db:
            test = Test(
                question=question,
                var_1=var_1,
                var_2=var_2,
                var_3=var_3,
                var_4=var_4,
                correct_answer=correct_answer,
                timer=timer,
                level=TestLevel(level),
                test_type=TestType(test_type)
            )
            db.add(test)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка при добавлении теста", exc_info=True)
        db.rollback()
        return False


def delete_test_db(test_id):
    try:
        with next(get_db()) as db:
            test = db.query(Test).filter_by(id=test_id).first()
            if not test:
                logger.info(f"Тест с ID: {test_id} не найден.")
                return False
            db.delete(test)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка при удалении теста", exc_info=True)
        db.rollback()
        return False


def change_test_db(test_id, question=None, var_1=None, var_2=None, var_3=None,
                   var_4=None, correct_answer=None, timer=None, level=None,
                   test_type=None):
    try:
        with next(get_db()) as db:
            test = db.query(Test).filter_by(id=test_id).first()
            if not test:
                logger.info(f"Тест с ID {test_id} не найден для обновлений.")
                return False
            change_test = {
                'question': question,
                'var_1': var_1,
                'var_2': var_2,
                'var_3': var_3,
                'var_4': var_4,
                'correct_answer': correct_answer,
                'timer': timer,
                'level': TestLevel(level),
                'test_type': TestType(test_type)
            }
            for key, value in change_test.items():
                if value is not None:
                    setattr(test, key, value)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка при изменении теста", exc_info=True)
        db.rollback()
        return False


def all_tests_db():
    try:
        with next(get_db()) as db:
            all_tests = db.query(Test).all()
            return all_tests
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении тестов из БД.", exc_info=True)
        return []


def all_level_tests_db(level):
    try:
        with next(get_db()) as db:
            level_tests = db.query(Test).filter_by(level=TestLevel(level)).all()
            return level_tests
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении тестов из БД.", exc_info=True)
        return []


def get_30_tests_train_db(level):
    try:
        with (next(get_db()) as db):
            subq = db.query(TestAttempt.test_id, func.count(TestAttempt.id).label("attempt_count")).group_by(TestAttempt.test_id).subquery()
            tests = (db.query(Test)
                     .outerjoin(subq, Test.id == subq.c.test_id)
                     .filter(Test.level == TestLevel(level))
                     .order_by(subq.c.attempt_count)
                     .limit(30)
                     .all())
            if len(tests) < 30:
                msg = 'Не достаточно тестов по этой теме для тренировки'
                logger.info(msg)
                return msg
            return tests
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении 30 тренировочных тестов", exc_info=True)
        return 'Ошибка при получении тестов'


def get_30_tests_exam_db(num_level_1=15, num_level_2=10, num_level_3=5):
    try:
        total = num_level_1 + num_level_2 + num_level_3
        if total != 30:
            msg = (f'Вы должны указать такое количество тестов каждого типа, чтобы их сумма равнялась 30. '
                   f'В вашем случае: 1: {num_level_1} + 2: {num_level_2} + 3: {num_level_3} = {total}')
            logger.info(msg)
            return msg
        with next(get_db()) as db:
            level_1 = db.query(Test).filter(Test.level == TestLevel.LEVEL_1).order_by(Test.id).limit(num_level_1).all()
            level_2 = db.query(Test).filter(Test.level == TestLevel.LEVEL_2).order_by(Test.id).limit(num_level_2).all()
            level_3 = db.query(Test).filter(Test.level == TestLevel.LEVEL_3).order_by(Test.id).limit(num_level_3).all()
            tests = level_1 + level_2 + level_3
            if len(tests) < 30:
                msg = f'В базе недостаточно тестов: найдено только {len(tests)} из 30'
                logger.info(msg)
                return msg
            random.shuffle(tests)
            return tests
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении 30 экзаменационных тестов", exc_info=True)
        return 'Ошибка при получении тестов для экзамена'
