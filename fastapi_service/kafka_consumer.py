import json
import asyncio
import redis.asyncio as redis
from kafka import KafkaConsumer
from .settings import settings
from .logger import logger
from .database import AsyncSessionLocal
from .crud import fetch_product

redis_client = redis.Redis(
    host= settings.REDIS_HOST,
    port= settings.REDIS_PORT,
    decode_responses=True,
)


async def start_kafka_consumer():
    consumer = None
    for _ in range(3):
        try:
            consumer = KafkaConsumer(
                'product_request',
                bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                group_id='fastapi-group',
                value_deserializer=lambda x: x.decode('utf-8'),
                auto_offset_reset="earliest",
            )
            logger.info("Успешно подключено к Kafka") 
            break
        except Exception as e:
            logger.warning(f"Ожидаем Kafka... {e}")
            await asyncio.sleep(5)

    loop = asyncio.get_event_loop()

    for _ in range(3):
        records = await loop.run_in_executor(None, consumer.poll, 1.0)
        for tp, messages in records.items():
            for message in messages:
                await handle_message(message)


async def handle_message(message):
    raw_msg = message.value

    if isinstance(raw_msg, bytes):  
        try:
            raw_msg = raw_msg.decode('utf-8')
            data = json.loads(raw_msg)
        except Exception as e:
            logger.warning(f"Ошибка при разборе сообщения: {e}")
            return
    elif isinstance(raw_msg, str):
        try:
            data = json.loads(raw_msg)
        except json.JSONDecodeError:
            logger.warning(f"Некорректный JSON: {raw_msg}")
            return
    elif isinstance(raw_msg, dict):
        data = raw_msg
    else:
        logger.warning(f"Неподдерживаемый формат: {type(raw_msg)}")
        return

    product_id = data.get("product_id")
    if not product_id:
        logger.warning("Нет product_id в сообщении")
        return

    async with AsyncSessionLocal() as db:
        product = await fetch_product(product_id, db)

    if product:
        await redis_client.set(f"product:{product_id}", json.dumps(product))
        logger.info(f"Товар {product_id} сохранён в Redis")
    else:
        logger.warning(f"Товар {product_id} не найден в базе данных")


