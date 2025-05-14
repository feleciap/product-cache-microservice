from django.shortcuts import render

import json
import redis
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from django.http import JsonResponse
from django.conf import settings
from loguru import logger

redis_client = None
producer = None

logger.add("logs.log", rotation="500 KB", level="INFO")

def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            db=0,
            decode_responses=True
        )
    return redis_client

def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
        except NoBrokersAvailable as e:
            logger("Kafka недоступна:", e)
            producer = None
    return producer

def get_product(request, product_id):
    redis_conn = get_redis()
    key = f"product:{product_id}"
    cached = redis_conn.get(key)

    if cached:
        return JsonResponse(json.loads(cached))
    
    kafka_prod = get_producer()
    if kafka_prod:
        message = {"product_id": product_id}
        kafka_prod.send('product_request', value=message)
        kafka_prod.flush()
    else:
        return JsonResponse({"error": "Kafka недоступен. Повторите позже."}, status=503)
    
    return JsonResponse({"status": "waiting for cache to be filled"})
