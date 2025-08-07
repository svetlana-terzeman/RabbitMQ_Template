from celery_app import celery_app
import time
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True)  # bind=True даёт доступ к self (информации о задаче)
def process_task(self, delay: int = 0):
    """
    Пример задачи для обработки:
    1. Принимает данные и искусственную задержку
    2. Имитирует обработку с задержкой
    3. Возвращает преобразованные данные
    """
    try:
        logger.info(f"Starting task {self.request.id}")

        # Искусственная задержка для тестирования таймаутов
        if delay > 0:
            logger.debug(f"Task {self.request.id} sleeping for {delay} sec")
            time.sleep(delay)

        # Основная "обработка" данных
        result = f"Запрос выполнен успешно"
        logger.info(f"Task {self.request.id} completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Task {self.request.id} failed: {str(e)}", exc_info=True)
        raise

