dev:
	docker-compose up --build

# Fast local tests (host Python, sqlite)
.PHONY: test-fast
test-fast:
	pytest -q

# Full test run with coverage
.PHONY: test-all
test-all:
	pytest --maxfail=1 --disable-warnings --cov -q

# Run tests in docker web service (assumes service name 'web')
.PHONY: test-docker
test-docker:
	docker-compose run --rm web pytest -q

# Lint & format (respect pre-commit config)
.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: resetdb
resetdb:
	python manage.py ensure_db

.PHONY: help
help:
	@echo "Targets:"
	@echo "  dev           - build & start docker-compose"
	@echo "  test-fast     - run fast local pytest"
	@echo "  test-all      - run full pytest with coverage"
	@echo "  test-docker   - run pytest inside docker web service"
	@echo "  lint          - run pre-commit on all files"
	@echo "  resetdb       - custom db ensure command"
	@echo "  help          - show this help"
