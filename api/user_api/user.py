from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database.userservice import *
from logging_config import logger

user_router = APIRouter(prefix="/ratings", tags=["Test Ratings"])


class AnswerSubmission(BaseModel):
    test_id: int
    timer: int
    user_response: str


@user_router.post("/answer")
async def submit_answer(answer: AnswerSubmission):
    result = user_get_answer_db(answer.test_id, answer.timer, answer.user_response)
    if result:
        return {"status": 1, "message": "Ответ сохранен."}
    logger.error(f"Ошибка при сохранении ответа для теста {answer.test_id}.")
    raise HTTPException(status_code=400, detail="Ошибка сохранения ответа.")


@user_router.get("/user/{user_id}")
async def get_user_ratings(user_id: int):
    result = user_test_rating_db(user_id)
    if isinstance(result, str):
        raise HTTPException(status_code=404, detail=result)
    return {"status": 1, "data": result}


@user_router.get("/user/{user_id}/{test_rating_id}/category")
async def get_category_rating(user_id: int, test_rating_id: int,
                              level: str = Query(..., description="Уровень теста (например, objects, actions, skills)"),
                              test_type: str = Query(..., description="Тип теста (например, type1, type2, type3)")):
    result = user_category_test_rating_db(user_id, test_rating_id, level, test_type)
    if result is None:
        raise HTTPException(status_code=404, detail="Не найден рейтинг для данной категории.")
    return {"status": 1, "data": result}


@user_router.get("/user/{user_id}/average")
async def get_user_average_rating(user_id: int,
                                  level: str = Query(..., description="Уровень теста"),
                                  test_type: str = Query(..., description="Тип теста")):
    result = user_all_tests_rating_db(user_id, level, test_type)
    if result is None:
        raise HTTPException(status_code=404, detail="Среднее значение рейтинга не найдено.")
    return {"status": 1, "data": result}


@user_router.get("/all/average")
async def get_all_users_average_rating(level: str = Query(..., description="Уровень теста"),
                                       test_type: str = Query(..., description="Тип теста")):
    result = all_users_tests_rating_db(level, test_type)
    if result is None:
        raise HTTPException(status_code=404, detail="Среднее значение рейтинга по всем пользователям не найдено.")
    return {"status": 1, "data": result}
