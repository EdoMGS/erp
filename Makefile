dev:
	docker-compose up --build

.PHONY: resetdb
resetdb:
	python manage.py ensure_db
