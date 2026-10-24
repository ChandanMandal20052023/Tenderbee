# Monorepo task automation

.PHONY: migrate test dev

# Migrations run strictly against Neon direct connection (DIRECT_URL)
migrate:
	DATABASE_URL=$${DIRECT_URL} python backend/manage.py migrate

# Development services startup
dev:
	docker compose up

# Run test suites across layers
test:
	python -m unittest discover -s core/engine/tests
	python backend/manage.py test backend
	npm --prefix frontend test
