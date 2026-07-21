run:
	uvicorn main:app --reload --port 8081

db-shell:
	docker exec -it postgres-db psql -U rafayyy -d subscription-app-db

db-up:
	docker-compose up -d

db-down:
	docker-compose down
