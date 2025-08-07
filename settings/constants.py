import os

RABBITMQ_HOST = 'rabbitmq'#os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = 'admin'#os.getenv('RABBITMQ_DEFAULT_USER', 'admin')
RABBITMQ_PASS = 'mq_pass'#os.getenv('RABBITMQ_DEFAULT_PASS', 'mq_pass')

PORT_AMQP =  5672#os.getenv('PORT_AMQP', '5672:5672').split(':')[-1]
PORT_WEB  = 15672#os.getenv('PORT_WEB', '15672:15672').split(':')[-1]

TASK_TIMEOUT               = 30#os.getenv('TASK_TIMEOUT', 10)
worker_concurrency         = 1#os.getenv('worker_concurrency', 1)