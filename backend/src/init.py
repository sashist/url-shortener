from src.connectors.rabbitmq_connector import RabbitManager
from src.connectors.redis_connector import RedisManager
from src.core.config import settings

redis_manager = RedisManager(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
rabbit_manager = RabbitManager(str(settings.RABBITMQ_URL))
