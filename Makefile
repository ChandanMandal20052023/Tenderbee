# Monorepo task automation

.PHONY: run migrate test

# Run local development environment
run:
	docker compose up

# Run migrations against Neon direct connection (DIRECT_URL)
migrate:
	DATABASE_URL=$${DIRECT_URL} python backend/manage.py migrate

# Run test suites across engine, backend apps, and frontend
test:
	python -m unittest discover -s backend/engine/tests
	python backend/manage.py test backend/apps
	npm --prefix frontend test
