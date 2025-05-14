# Product Cache Microservice

## Описание

Проект демонстрирует архитектуру микросервисов с использованием **Django** и **FastAPI**, в связке с **Kafka**, **Redis** и **PostgreSQL**.  

Django API принимает запрос на товар, отправляет событие в Kafka. FastAPI-потребитель обрабатывает Kafka-сообщение, извлекает товар из базы и сохраняет его в Redis. Повторный запрос отдаёт данные из кеша.

## Архитектура

Client --> Django (API) --> Kafka --> FastAPI --> PostgreSQL --> Redis --> Django (cached response)


## Стек технологий

- **Django** — API для получения товара
- **FastAPI** — Kafka consumer + обработка товара
- **Redis** — Кеш
- **Kafka** — Очередь запросов на получение товара
- **PostgreSQL** — Хранилище товаров
- **Docker + docker-compose** — Оркестрация сервисов

---

## Структура проекта

project1/

├── backend/ # Django проект

│ └── productapp/ # Django-приложение

├── fastapi_service/ # FastAPI-сервис

├── .env # Секреты (не добавлять в git)

├── .env.example # Пример переменных окружения

├── docker-compose.yml

└── README.md


## Переменные окружения (`.env`)

Создайте файл `.env` (или используйте `.env.example`):

    .env
    DB_NAME=your_db
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_HOST=postgres
    DB_PORT=5432

    REDIS_HOST=redis
    REDIS_PORT=6379

    KAFKA_BOOTSTRAP=kafka:9092
    KAFKA_BROKER_ID=1
    KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
    KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
    KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092
    KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1

    DJANGO_DELAY=10
    FASTAPI_DELAY=15



## Запуск

`docker-compose --env-file .env up --build`

## Порты по умолчанию:

    Django: http://localhost:8000

    FastAPI: http://localhost:8001

    Kafka: localhost:9092

    Redis: localhost:6379

    PostgreSQL: localhost:5433

## Пример работы

Сделай GET запрос на http://localhost:8000/productapp/1/

Django отправит сообщение в Kafka

FastAPI прочитает Kafka, найдёт продукт в PostgreSQL, и положит в Redis

Повторный запрос вернёт кешированные данные из Redis

## Тест данных

Можно создать продукт вручную:

`docker exec -it project1_django_backend_1 python manage.py shell`

`>>> from productapp.models import Product`

`>>> Product.objects.create(name="Test Product", price=123.45, description="A test product")`
