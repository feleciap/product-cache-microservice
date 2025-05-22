COMPOSE=sudo docker-compose -f docker-compose.infra.yml -f docker-compose.django.yml -f docker-compose.fastapi.yml

.PHONY: up down restart logs rebuild

up:
	$(COMPOSE) up 

down:
	$(COMPOSE) down -v

restart:
	$(MAKE) down
	$(MAKE) up

logs:
	$(COMPOSE) logs -f

rebuild:
	$(COMPOSE) down -v
	$(COMPOSE) up --build 