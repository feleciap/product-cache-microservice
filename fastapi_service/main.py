import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .kafka_consumer import start_kafka_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(start_kafka_consumer())
    yield
    task.cancel()
    await asyncio.sleep(5)

app = FastAPI(lifespan=lifespan)
