.PHONY:run
run:
	python manage.py runserver

.PHONY:migrate
migrate:
	python manage.py makemigrations; python manage.py migrate

.PHONY:save-required
save-require:
	pip freeze > requirements.txt

.PHONY: install-required
install-required:
	pip install -r requirements.txt

.PHONY: update
update: install-required migrate

.PHONY: delete-migrations
delete-migrations: 
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/.venv/*" -delete

.PHONY: import-user
import-user:
	python manage.py loaddata db.json

.PHONY: seed
seed:
	if [ "$(a)" ]; then \
		if [ "$(n)" ]; then \
			python manage.py seed $(a) --number=$(n); \
		else \
			python manage.py seed $(a); \
		fi \
	else \
		echo "Argument 'a' is required"; \
	fi