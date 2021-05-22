build: # Сборка образа
	docker-compose build
up: # Создание и запуск контейнера
	docker-compose up -d
stop: # Остановка контейнера
	docker-compose stop
start: # Запуск контейнера
	docker-compose start			
clean: # Остановка и удаление контейнеров
	docker-compose down
			
# docker rm $(docker ps -a -q)
# docker rmi $(docker images -a -q)
# docker volume rm $(docker volume ls -q)
# docker network rm $(docker network ls -q)
# docker system prune -fa