from database import get_db
from database.models import Admin, User, TestRating
from sqlalchemy.exc import SQLAlchemyError
import bcrypt
from logging_config import logger


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def admin_registration_db(admin_first_name, admin_last_name, number, password):
    hashed_password = hash_password(password)
    try:
        with next(get_db()) as db:
            logger.info(f"Проверка существования админа с номером: '{number}'")
            existing_admin = db.query(Admin).filter_by(number=number).first()
            if existing_admin:
                logger.info(f"Админ с номером: {number} уже существует.")
                return False
            admin = Admin(
                admin_first_name=admin_first_name,
                admin_last_name=admin_last_name,
                number=number,
                password=hashed_password
            )
            db.add(admin)
            db.commit()
            logger.info(f"Регистрация админа {number} прошла успешно.")
            return True
    except SQLAlchemyError as e:
        logger.error("Error in admin_registration, performing rollback", exc_info=True)
        db.rollback()
        return False


def user_registration_db(user_first_name, user_last_name, number,
                         par_first_name, par_last_name, par_number,
                         birthday, school_class, university, group_number, password):
    hashed_password = hash_password(password)
    try:
        with next(get_db()) as db:
            existing_user = db.query(User).filter_by(number=number).first()
            if existing_user:
                logger.info(f"Пользователь с номером {number} уже существует.")
                return False
            user = User(
                user_first_name=user_first_name,
                user_last_name=user_last_name,
                number=number,
                par_first_name=par_first_name,
                par_last_name=par_last_name,
                par_number=par_number,
                birthday=birthday,
                school_class=school_class,
                university=university,
                group_number=group_number,
                password=hashed_password
            )
            db.add(user)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка регистрации", exc_info=True)
        db.rollback()
        return False


def admin_delete_db(admin_id):
    try:
        with next(get_db()) as db:
            admin = db.query(Admin).filter_by(id=admin_id).first()
            if not admin:
                logger.info(f"Админ с ID: {admin_id} не найден.")
                return False
            db.delete(admin)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Error in admin_delete, performing rollback", exc_info=True)
        db.rollback()
        return False


def user_delete_db(user_id):
    try:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                logger.info(f"Пользователь с ID: {user_id} не найден.")
                return False
            db.delete(user)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка при удалении пользователя", exc_info=True)
        db.rollback()
        return False


def block_user_db(user_id):
    try:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                logger.info(f"Пользователь с ID: {user_id} не найден.")
                return False
            user.is_blocked = True
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка во время блокировки пользователя", exc_info=True)
        db.rollback()
        return False


def unblock_user_db(user_id):
    try:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                logger.info(f"Пользователь с ID: {user_id} для разблокировки не найден.")
                return False
            user.is_blocked = False
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка во время разблокировки пользователя", exc_info=True)
        db.rollback()
        return False


def change_user_data_db(user_id, user_first_name=None, user_last_name=None,
                        number=None, par_first_name=None, par_last_name=None,
                        par_number=None, birthday=None, school_class=None,
                        university=None, group_number=None):
    try:
        with next(get_db()) as db:
            user = db.query(User).filter_by(id=user_id).first()
            if not user:
                logger.info(f"Пользователь с ID: {user_id} для обновления данных не найден.")
                return False
            user_change_data = {
                'user_first_name': user_first_name,
                'user_last_name': user_last_name,
                'number': number,
                'par_first_name': par_first_name,
                'par_last_name': par_last_name,
                'par_number': par_number,
                'birthday': birthday,
                'school_class': school_class,
                'university': university,
                'group_number': group_number
            }
            for key, value in user_change_data.items():
                if value is not None:
                    setattr(user, key, value)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка при обновлении данных пользователя", exc_info=True)
        db.rollback()
        return False


def change_admin_data_db(admin_id, admin_first_name=None, admin_last_name=None,
                         number=None):
    try:
        with next(get_db()) as db:
            admin = db.query(Admin).filter_by(id=admin_id).first()
            if not admin:
                logger.info(f"Админ с ID: {admin_id} для обновления данных не найден.")
                return False
            admin_change_data = {
                'admin_first_name': admin_first_name,
                'admin_last_name': admin_last_name,
                'number': number
            }
            for key, value in admin_change_data.items():
                if value is not None:
                    setattr(admin, key, value)
            db.commit()
            return True
    except SQLAlchemyError as e:
        logger.error("Ошибка при обновлении данных админа", exc_info=True)
        db.rollback()
        return False


def serialize_total_rating_db(total_rating):
    if hasattr(total_rating, 'to_dict'):
        return total_rating.to_dict()
    else:
        return {col.name: getattr(total_rating, col.name) for col in total_rating.__table__.columns}


def get_user_test_statistic_db(total_rating_id):
    with next(get_db()) as db:
        test_statistic = db.query(TestRating).filter_by(id=total_rating_id).first()
        return serialize_total_rating_db(test_statistic) if test_statistic else {}


def get_user_statistic_db(user_id):
    with next(get_db()) as db:
        user_statistic = db.query(TestRating).filter_by(user_id=user_id).first()
        return serialize_total_rating_db(user_statistic) if user_statistic else {}


def get_full_statistic_db():
    with next(get_db()) as db:
        full_statistic = db.query(TestRating).all()
        return [serialize_total_rating_db(stat) for stat in full_statistic]
    