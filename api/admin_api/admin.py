from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.adminservice import *
from logging_config import logger


class AdminCreate(BaseModel):
    admin_first_name: str
    admin_last_name: str
    number: str
    password: str


class UserCreate(BaseModel):
    user_first_name: str
    user_last_name: str
    number: str
    password: str
    par_first_name: str
    par_last_name: str = None
    par_number: str
    birthday: str = None
    school_class: int = None
    university: str = None
    group_number: str = None


class ChangeUserData(BaseModel):
    user_first_name: str = None
    user_last_name: str = None
    number: str = None
    par_first_name: str = None
    par_last_name: str = None
    par_number: str = None
    birthday: str = None
    school_class: int = None
    university: str = None
    group_number: str = None


class ChangeAdminData(BaseModel):
    admin_first_name: str = None
    admin_last_name: str = None
    number: str = None


admin_router = APIRouter(prefix='/admins', tags=['Админы'])


@admin_router.post('/admin_registration')
async def register_admin(admin: AdminCreate):
    result = admin_registration_db(
        admin.admin_first_name,
        admin.admin_last_name,
        admin.number,
        admin.password
    )
    if result:
        logger.info(f"Админ {admin.number} зарегистрирован успешно.")
        return {'status': 1, 'message': 'Админ зарегистрирован успешно'}
    raise HTTPException(status_code=400, detail='Ошибка регистрации админа')


@admin_router.delete('/{admin_id}')
async def delete_admin(admin_id: int):
    result = admin_delete_db(admin_id)
    if result:
        logger.info(f"Админ с id {admin_id} удалён.")
        return {'status': 1, 'message': f'Админ с id {admin_id} удалён'}
    raise HTTPException(status_code=404, detail='Админ не найден или ошибка удаления')


@admin_router.put('/{admin_id}')
async def update_admin(admin_id: int, admin_data: ChangeAdminData):
    result = change_admin_data_db(
        admin_id,
        admin_data.admin_first_name,
        admin_data.admin_last_name,
        admin_data.number
    )
    if result:
        logger.info(f"Данные админа с id {admin_id} обновлены.")
        return {'status': 1, 'message': f'Данные админа с id {admin_id} обновлены'}
    raise HTTPException(status_code=400, detail='Ошибка обновления данных админа')


@admin_router.post('/user_registration')
async def register_user(user: UserCreate):
    result = user_registration_db(
        user_first_name=user.user_first_name,
        user_last_name=user.user_last_name,
        number=user.number,
        par_first_name=user.par_first_name,
        par_last_name=user.par_last_name,
        par_number=user.par_number,
        birthday=user.birthday,
        school_class=user.school_class,
        university=user.university,
        group_number=user.group_number,
        password=user.password
    )
    if result:
        return {'status': 1, 'message': 'Пользователь зарегистрирован успешно'}
    raise HTTPException(status_code=400, detail='Ошибка регистрации пользователя')


@admin_router.delete('/user_del/{user_id}')
async def delete_user(user_id: int):
    result = user_delete_db(user_id)
    if result:
        return {'status': 1, 'message': f'Пользователь с id {user_id} удалён'}
    raise HTTPException(status_code=404, detail='Пользователь не найден или ошибка удаления')


@admin_router.post('/user_block/{user_id}/block')
async def block_user(user_id: int):
    result = block_user_db(user_id)
    if result:
        return {'status': 1, 'message': f'Пользователь с id {user_id} заблокирован'}
    raise HTTPException(status_code=400, detail='Ошибка блокировки пользователя')


@admin_router.post('/user_unblock/{user_id}')
async def unblock_user(user_id: int):
    result = unblock_user_db(user_id)
    if result:
        return {'status': 1, 'message': f'Пользователь с id {user_id} разблокирован'}
    raise HTTPException(status_code=400, detail='Ошибка разблокировки пользователя')


@admin_router.put('/user_update/{user_id}')
async def update_user(user_id: int, user_data: ChangeUserData):
    result = change_user_data_db(
        user_id,
        user_first_name=user_data.user_first_name,
        user_last_name=user_data.user_last_name,
        number=user_data.number,
        par_first_name=user_data.par_first_name,
        par_last_name=user_data.par_last_name,
        par_number=user_data.par_number,
        birthday=user_data.birthday,
        school_class=user_data.school_class,
        university=user_data.university,
        group_number=user_data.group_number
    )
    if result:
        return {'status': 1, 'message': f'Данные пользователя с id {user_id} обновлены'}
    raise HTTPException(status_code=400, detail='Ошибка обновления данных пользователя')


@admin_router.get('/user_test/{total_rating_id}')
async def get_user_test_statistic(total_rating_id: int):
    result = get_user_test_statistic_db(total_rating_id)
    if result:
        return {'status': 1, 'data': result}
    raise HTTPException(status_code=404, detail='Статистика теста не найдена')


@admin_router.get('/user/{user_id}')
async def get_user_statistic(user_id: int):
    result = get_user_statistic_db(user_id)
    if result:
        return {'status': 1, 'data': result}
    raise HTTPException(status_code=404, detail='Статистика пользователя не найдена')


@admin_router.get('/full')
async def get_full_statistic():
    result = get_full_statistic_db()
    if result:
        return {'status': 1, 'data': result}
    raise HTTPException(status_code=404, detail='Общая статистика не найдена')
