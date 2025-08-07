# Импорт необходимых библиотек
from celery import Celery  # Основной класс Celery для создания приложения
import logging  # Модуль для логирования событий
import sys  # Для работы с системными потоками ввода/вывода
from settings.constants import RABBITMQ_USER, RABBITMQ_HOST, RABBITMQ_PASS,  PORT_AMQP, TASK_TIMEOUT, worker_concurrency

# Настройка системы логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Создаем логгер для текущего модуля
logger = logging.getLogger(__name__)

# Инициализация Celery приложения
celery_app = Celery(
    'tasks',  # Основное имя приложения (используется для именования очередей)

    # URL для подключения к брокеру сообщений (RabbitMQ)
    # Формат: amqp://логин:пароль@хост:порт//
    broker=f'amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{PORT_AMQP}//',

    # Бэкенд для хранения результатов задач
    # rpc:// означает использование RabbitMQ для возврата результатов
    backend='rpc://',

    # Список модулей, содержащих задачи Celery
    include=['tasks']
)

# Конфигурация Celery приложения
celery_app.conf.update(

    # Максимальное время выполнения задачи в секундах
    # task_time_limit=TASK_TIMEOUT,
    task_soft_time_limit=TASK_TIMEOUT,

    # Формат сериализации задач при отправке в очередь
    task_serializer='json',

    # Формат сериализации результатов выполнения задач
    result_serializer='json',

    # Список разрешенных форматов для входящих сообщений
    accept_content=['json'],

    # Часовой пояс для планировщика задач
    timezone='Europe/Moscow',  # Устанавливаем московский часовой пояс

    # Принудительное использование UTC времени
    enable_utc=False,

    # Настройка поведения воркеров:
    # каждый воркер будет брать worker_prefetch_multiplier задач за раз
    worker_prefetch_multiplier=1,
    worker_concurrency=worker_concurrency, #Количество процессов (воркеров)

    # Дополнительные рекомендуемые параметры:
    task_track_started=True,         # Включаем отслеживание времени начала выполнения задачи
    worker_max_tasks_per_child=100,  # Перезапуск воркера после 100 задач
    task_acks_late=True,             # Подтверждение задач после выполнения, а не до
    task_reject_on_worker_lost=True, # Задача будет возвращена в очередь при падении воркера
    result_extended=True,            # Включаем расширенную информацию о результате
    worker_cancel_long_running_tasks_on_connection_loss=True  # Отмена задач при потере соединения
)
celery_app.conf.broker_transport_options = {
    'max_retries': 0,
    }