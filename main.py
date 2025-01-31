# Импортируем необходимые библиотеки
import time  # Для измерения времени выполнения запросов
from typing import List  # Для аннотации типов (списков)
from fastapi import FastAPI, HTTPException, Request, Response  # FastAPI для создания API
from pydantic import HttpUrl  # Для валидации URL
from schemas.request import PredictionRequest, PredictionResponse  # Схемы запроса и ответа
from utils.logger import setup_logger  # Логгер для логирования событий

# Инициализация FastAPI приложения
app = FastAPI()
logger = None  # Глобальная переменная для логгера


@app.on_event("startup")
async def startup_event():
    """
    Событие, которое выполняется при запуске приложения.
    Инициализирует логгер.
    """
    global logger
    logger = await setup_logger()  # Настраиваем логгер


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware для логирования входящих запросов и ответов.
    
    :param request: Входящий HTTP-запрос.
    :param call_next: Функция для вызова следующего middleware или обработчика запроса.
    :return: HTTP-ответ.
    """
    start_time = time.time()  # Засекаем время начала обработки запроса

    # Логируем входящий запрос
    body = await request.body()  # Получаем тело запроса
    await logger.info(
        f"Incoming request: {request.method} {request.url}\n"
        f"Request body: {body.decode()}"  # Логируем метод, URL и тело запроса
    )

    # Вызываем следующий middleware или обработчик запроса
    response = await call_next(request)
    process_time = time.time() - start_time  # Вычисляем время обработки запроса

    # Получаем тело ответа
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    # Логируем завершение запроса
    await logger.info(
        f"Request completed: {request.method} {request.url}\n"
        f"Status: {response.status_code}\n"  # Логируем статус ответа
        f"Response body: {response_body.decode()}\n"  # Логируем тело ответа
        f"Duration: {process_time:.3f}s"  # Логируем время выполнения запроса
    )

    # Возвращаем ответ клиенту
    return Response(
        content=response_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )


@app.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    """
    Обработчик POST-запросов на эндпоинт /api/request.
    Принимает запрос, обрабатывает его и возвращает ответ.
    
    :param body: Данные запроса в формате PredictionRequest.
    :return: Ответ в формате PredictionResponse.
    """
    try:
        # Логируем начало обработки запроса
        await logger.info(f"Processing prediction request with id: {body.id}")

        # Здесь будет вызов вашей модели для обработки запроса
        # В данном примере используется заглушка
        answer = 1  # Замените на реальный вызов модели

        # Пример источников (URL), которые могут быть возвращены в ответе
        sources: List[HttpUrl] = [
            HttpUrl("https://itmo.ru/ru/"),
            HttpUrl("https://abit.itmo.ru/"),
        ]

        # Формируем ответ
        response = PredictionResponse(
            id=body.id,  # ID запроса
            answer=answer,  # Ответ модели
            reasoning="Из информации на сайте",  # Обоснование ответа
            sources=sources,  # Список источников
        )

        # Логируем успешное завершение обработки запроса
        await logger.info(f"Successfully processed request {body.id}")
        return response  # Возвращаем ответ клиенту
    except ValueError as e:
        # Обработка ошибок валидации
        error_msg = str(e)
        await logger.error(f"Validation error for request {body.id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)  # Возвращаем ошибку 400
    except Exception as e:
        # Обработка внутренних ошибок сервера
        await logger.error(f"Internal error processing request {body.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")  # Возвращаем ошибку 500