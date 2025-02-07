from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database.testservice import *
from logging_config import logger


class TestCreate(BaseModel):
    question: str
    var_1: str
    var_2: str
    var_3: str
    var_4: str
    correct_answer: str
    timer: int
    level: str  # например, "objects", "actions", "skills"
    test_type: str  # например, "type1", "type2", "type3"


class TestUpdate(BaseModel):
    question: str = None
    var_1: str = None
    var_2: str = None
    var_3: str = None
    var_4: str = None
    correct_answer: str = None
    timer: int = None
    level: str = None
    test_type: str = None


test_router = APIRouter(prefix='/tests', tags=['Тесты'])


@test_router.post('/', response_model=dict)
async def create_test(test: TestCreate):
    result = add_test_db(
        question=test.question,
        var_1=test.var_1,
        var_2=test.var_2,
        var_3=test.var_3,
        var_4=test.var_4,
        correct_answer=test.correct_answer,
        timer=test.timer,
        level=test.level,
        test_type=test.test_type
    )
    if result:
        logger.info("Тест успешно добавлен.")
        return {"status": 1, "message": "Тест успешно добавлен."}
    logger.error("Ошибка при добавлении теста.")
    raise HTTPException(status_code=400, detail="Ошибка при добавлении теста.")


@test_router.delete('/{test_id}', response_model=dict)
async def delete_test(test_id: int):
    result = delete_test_db(test_id)
    if result:
        logger.info(f"Тест с id {test_id} успешно удалён.")
        return {"status": 1, "message": f"Тест с id {test_id} удалён."}
    logger.error(f"Тест с id {test_id} не найден или ошибка удаления.")
    raise HTTPException(status_code=404, detail="Тест не найден или ошибка удаления.")


@test_router.put('/{test_id}', response_model=dict)
async def update_test(test_id: int, test_data: TestUpdate):
    result = change_test_db(
        test_id,
        question=test_data.question,
        var_1=test_data.var_1,
        var_2=test_data.var_2,
        var_3=test_data.var_3,
        var_4=test_data.var_4,
        correct_answer=test_data.correct_answer,
        timer=test_data.timer,
        level=test_data.level,
        test_type=test_data.test_type
    )
    if result:
        logger.info(f"Данные теста с id {test_id} успешно обновлены.")
        return {"status": 1, "message": f"Тест с id {test_id} обновлён."}
    logger.error("Ошибка обновления теста.")
    raise HTTPException(status_code=400, detail="Ошибка обновления теста.")


@test_router.get('/', response_model=dict)
async def get_all_tests():
    tests = all_tests_db()
    logger.info(f"Получено {len(tests)} тестов.")
    return {"status": 1, "data": tests}


@test_router.get('/level/{level}', response_model=dict)
async def get_tests_by_level(level: str):
    tests = all_level_tests_db(level)
    logger.info(f"Получено {len(tests)} тестов для уровня {level}.")
    return {"status": 1, "data": tests}


@test_router.get('/train/{level}', response_model=dict)
async def get_train_tests(level: str):
    result = get_30_tests_train_db(level)
    if isinstance(result, str):
        logger.info(result)
        raise HTTPException(status_code=400, detail=result)
    logger.info(f"Получено 30 тестов для тренировки уровня {level}.")
    return {"status": 1, "data": result}


@test_router.get('/exam', response_model=dict)
async def get_exam_tests(
    num_level_1: int = Query(15, ge=0),
    num_level_2: int = Query(10, ge=0),
    num_level_3: int = Query(5, ge=0)
):
    result = get_30_tests_exam_db(num_level_1, num_level_2, num_level_3)
    if isinstance(result, str):
        logger.info(result)
        raise HTTPException(status_code=400, detail=result)
    return {"status": 1, "data": result}
