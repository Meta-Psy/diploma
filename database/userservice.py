from database import get_db
from database.models import UserAnswer, TestRating, Test
from sqlalchemy.exc import SQLAlchemyError
from logging_config import logger
import bcrypt


def user_get_answer_db(test_id: int, timer: int, user_response: str):
    try:
        with next(get_db()) as db:
            test = db.query(Test).filter_by(id=test_id).first()
            if not test:
                logger.info(f"Тест с ID {test_id} не найден.")
                return False
            is_correct = (user_response == test.correct_answer)
            last_answer = db.query(UserAnswer).filter(UserAnswer.test_id == test_id) \
                .order_by(UserAnswer.attempt.desc()).first()
            if last_answer is None:
                attempt_count = 1
            else:
                attempt_count = last_answer.attempt + 1
            answer = UserAnswer(
                user_response=user_response,
                correctness=is_correct,
                attempt=attempt_count,
                timer=timer,
                test_id=test_id
            )
            db.add(answer)
            db.commit()
            logger.info(f"Сохранен ответ для теста ID {test_id}, попытка {attempt_count}, правильность: {is_correct}.")
            return True
    except SQLAlchemyError as e:
        logger.error("Произошла ошибка при сохранении ответа пользователя.", exc_info=True)
        db.rollback()
        return False


def user_test_rating_db(user_id: int):
    try:
        with next(get_db()) as db:
            ratings = db.query(TestRating).filter_by(user_id=user_id).all()
            if ratings:
                logger.info(f"Найдено {len(ratings)} записей рейтинга для пользователя с ID {user_id}.")
                return ratings
            else:
                logger.info(f"Рейтингов для пользователя с ID {user_id} не найдено.")
                return "Ошибка получения статистики о данном тесте"
    except SQLAlchemyError as e:
        logger.error("Ошибка в функции получения рейтинга за тест.", exc_info=True)
        return "Ошибка при выполнении запроса статистики"


def user_category_test_rating_db(user_id: int, test_rating_id: int, level: str, test_type: str):
    try:
        with next(get_db()) as db:
            rating = db.query(TestRating).filter_by(user_id=user_id, id=test_rating_id).first()
            if rating:
                attr_name = f'category_{level}_{test_type}'
                value = getattr(rating, attr_name, None)
                if value is not None:
                    logger.info(f"Для рейтинга ID {test_rating_id} найден атрибут {attr_name} со значением {value}.")
                    return value
                else:
                    logger.info(f"Атрибут {attr_name} не найден в рейтинге с ID {test_rating_id}.")
                    return None
            else:
                logger.info(f"Рейтинг с ID {test_rating_id} для пользователя с ID {user_id} не найден.")
                return None
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении рейтинга по категории.", exc_info=True)
        return None


def user_all_tests_rating_db(user_id: int, level: str, test_type: str):
    try:
        with next(get_db()) as db:
            ratings = db.query(TestRating).filter_by(user_id=user_id).all()
            if ratings:
                attr_name = f'category_{level}_{test_type}'
                values = [getattr(r, attr_name, None) for r in ratings if getattr(r, attr_name, None) is not None]
                if values:
                    avg_value = sum(values) / len(values)
                    logger.info(f"Среднее значение {attr_name} для пользователя с ID {user_id} равно {avg_value}.")
                    return avg_value
                else:
                    logger.info(f"Для пользователя с ID {user_id} не найдено значений атрибута {attr_name}.")
                    return None
            else:
                logger.info(f"У пользователя с ID {user_id} нет записей рейтинга.")
                return None
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении рейтинга всех тестов для пользователя.", exc_info=True)
        return None


def all_users_tests_rating_db(level: str, test_type: str):
    try:
        with next(get_db()) as db:
            ratings = db.query(TestRating).all()
            if ratings:
                attr_name = f'category_{level}_{test_type}'
                values = [getattr(r, attr_name, None) for r in ratings if getattr(r, attr_name, None) is not None]
                if values:
                    avg_value = sum(values) / len(values)
                    logger.info(f"Среднее значение {attr_name} по всем пользователям равно {avg_value}.")
                    return avg_value
                else:
                    logger.info(f"Для атрибута {attr_name} в рейтингах ничего не найдено.")
                    return None
            else:
                logger.info("Нет записей в рейтинге тестов.")
                return None
    except SQLAlchemyError as e:
        logger.error("Ошибка при получении рейтинга всех пользователей.", exc_info=True)
        return None


def change_password_db(user_id, password):
    pass
