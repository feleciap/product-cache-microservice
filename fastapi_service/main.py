import os
import json
import asyncio
import redis.asyncio as redis
from kafka import KafkaConsumer
from loguru import logger
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()
logger.add("logs.log", rotation="500 KB", level="INFO")

app = FastAPI()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis",),
    port=int(os.getenv("REDIS_PORT", 6379)), 
    decode_responses=True,
)

DATABASE_URL = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def fetch_product(product_id: int, db:AsyncSession):
    result = await db.execute(
        text("SELECT id, name, price, description FROM productapp_product WHERE id = :id"),
        {"id": product_id}
    )
    row = result.fetchone()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "price": float(row[2]),
            "description": row[3]
        }
    return None

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_kafka_consumer())


async def start_kafka_consumer():
    consumer = None
    while True:
        try:
            consumer = KafkaConsumer(
                'product_request',
                bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP", "kafka:9092"),
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

    while True:
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