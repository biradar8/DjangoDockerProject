# --- Configurable Variables (can override via CLI) ---
SERVICE ?= web
DJANGO_CMD ?= python manage.py
DC ?= docker-compose

# App-level
USERNAME ?= nexg
EMAIL ?= nexg@localhost.com
COUNT ?= 100

# DB
DB_USER ?= postgres
DB_PORT ?= 5432
PRIMARY_DB ?= primary
REPLICA_DB ?= replica

# Set the default goal to 'help' so typing 'make' shows the menu
.DEFAULT_GOAL := help

.PHONY: help up down migrate migrations collectstatic superuser seed-posts test check-primary-db check-replica-db bash promote-replica logs-db

help: ## 🛟 Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# --- Docker Lifecycle ---

up: ## 🚀 Start the containers in the background
	$(DC) up -d --build

down: ## 🛑 Stop and remove containers, networks
	$(DC) down

# --- Django Commands ---

migrate: ## 🗄️ Run Django migrations
	$(DC) exec $(SERVICE) $(DJANGO_CMD) migrate

migrations: ## 📝 Generate new Django migrations
	$(DC) exec $(SERVICE) $(DJANGO_CMD) makemigrations

collectstatic: ## 🎨 Generate static files
	$(DC) exec $(SERVICE) $(DJANGO_CMD) collectstatic --noinput --clear

superuser: ## 🦸 Create a default superuser (nexg)
	$(DC) exec $(SERVICE) $(DJANGO_CMD) createsuperuser --username $(USERNAME) --email $(EMAIL)

seed-posts: ## 🌱 Seed the database with fake posts
	$(DC) exec $(SERVICE) $(DJANGO_CMD) seed_posts --count $(COUNT) --username $(USERNAME)

test: ## 🧪 Run the pytest suite
	$(DC) exec $(SERVICE) pytest

bash: ## 💻 Open a bash shell inside the container
	$(DC) exec $(SERVICE) bash

# --- Database Management ---

check-primary-db: ## 🔍 Check primary database readiness
	$(DC) exec $(PRIMARY_DB) pg_isready -h $(PRIMARY_DB) -p $(DB_PORT) -U $(DB_USER)

check-replica-db: ## 🔍 Check replica database readiness
	$(DC) exec $(REPLICA_DB) pg_isready -h $(REPLICA_DB) -p $(DB_PORT) -U $(DB_USER)

logs-db: ## 📜 Tail the logs for both databases
	$(DC) logs -f $(PRIMARY_DB) $(REPLICA_DB)

promote-replica: ## 👑 Emergency: Promote the Replica to Primary
	@echo "Promoting the replica database to primary..."
	docker-compose exec -u postgres replica pg_ctl promote -D /var/lib/postgresql/data
	$(DC) exec -u $(DB_USER) $(REPLICA_DB) pg_ctl promote -D /var/lib/postgresql/data
	@echo "Promotion signal sent! Don't forget to update your Django .env to point to the new primary."