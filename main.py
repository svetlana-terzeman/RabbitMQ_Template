# Импорты необходимых библиотек
from fastapi import FastAPI, HTTPException
from celery.result import AsyncResult
from concurrent.futures import ThreadPoolExecutor
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tasks import process_task
import logging
import time
import asyncio
import sys
from settings.constants import TASK_TIMEOUT

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asasctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()

class TaskRequest(BaseModel):
    delay: int = 0  # Искусственная задержка для тестирования


@app.post("/process", response_model=dict)
async def process_request(request: TaskRequest):
    """
    Единственный эндпоинт, который:
    1. Принимает запрос
    2. Ставит задачу в очередь Celery
    3. Ожидает результат с таймаутом 30 секунд
    4. Возвращает либо результат, либо просьбу повторить позже
    """
    try:
        # Отправляем задачу в Celery через RabbitMQ
        task = process_task.delay(request.delay)
        logger.info(f"Поступил новый запрос ID: {task.id}")

        # Настраиваем таймаут ожидания
        start_time = time.time()
        check_interval = 0.5  # Проверяем статус каждые 0.5 секунды

        while True:
            # Проверяем, не истёк ли таймаут
            if time.time() - start_time > TASK_TIMEOUT:
                logger.warning(f"Время ожидания истекло для task {task.id}")
                task.revoke(terminate=True, signal='SIGKILL')
                return JSONResponse(
                    status_code=202,
                    content={
                        "status": "pending",
                        "message": "Пока не можем обработать ваш запрос, попробуйте позже",
                        "time": time.time() - start_time  # Даём ID для возможного отслеживания
                    }
                )

            # Проверяем статус задачи в Celery
            result = AsyncResult(task.id)

            if result.ready():  # Задача завершена (успешно или с ошибкой)
                if result.successful():
                    logger.info(f"Task {task.id} completed successfully")
                    return {
                        "status": "completed",
                        "result": result.result,
                        "time": time.time() - start_time
                    }
                else:
                    # Задача завершилась с ошибкой
                    logger.error(f"Task {task.id} failed: {result.result}")
                    raise HTTPException(
                        status_code=500,
                        detail={
                            "status": "failed",
                            "error": str(result.result),
                            "task_id": task.id
                        }
                    )

            # Если задача ещё не готова, ждём перед следующей проверкой
            # Используем asyncio.sleep вместо time.sleep для асинхронности
            await asyncio.sleep(check_interval)

    except Exception as e:
        logger.error(f"Ошибка сервиса: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Internal server error",
                "error": str(e)

            }
        )
