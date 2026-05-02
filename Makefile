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
	docker-compose up -d --build

down: ## 🛑 Stop and remove containers, networks, and volumes
	docker-compose down

# --- Django Commands ---

migrate: ## 🗄️ Run Django migrations
	docker-compose exec web python manage.py migrate

migrations: ## 📝 Generate new Django migrations
	docker-compose exec web python manage.py makemigrations

collectstatic: ## 🎨 Generate static files
	docker-compose exec web python manage.py collectstatic --noinput --clear

superuser: ## 🦸 Create a default superuser (nexg)
	docker-compose exec web python manage.py createsuperuser --username nexg --email nexg@localhost.com

seed-posts: ## 🌱 Seed the database with fake posts
	docker-compose exec web python manage.py seed_posts

test: ## 🧪 Run the pytest suite
	docker-compose exec web pytest

bash: ## 💻 Open a bash shell inside the web container
	docker-compose exec web bash

# --- Database Management ---

check-primary-db: ## 🔍 Check primary database readiness
	docker-compose exec primary pg_isready -h primary -p 5432 -U postgres

check-replica-db: ## 🔍 Check replica database readiness
	docker-compose exec replica pg_isready -h replica -p 5432 -U postgres

logs-db: ## 📜 Tail the logs for both databases
	docker-compose logs -f primary replica

promote-replica: ## 👑 Emergency: Promote the Replica to Primary
	@echo "Promoting the replica database to primary..."
	docker-compose exec -u postgres replica pg_ctl promote -D /var/lib/postgresql/data
	@echo "Promotion signal sent! Don't forget to update your Django .env to point to the new primary."