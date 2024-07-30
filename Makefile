.PHONY:run
run:
	poetry run python -m healthharmony.manage runserver

.PHONY:migrate
migrate:
	poetry run python -m healthharmony.manage makemigrations
	poetry run python -m healthharmony.manage migrate

.PHONY: install
install:
	poetry install

.PHONY: update
update: install migrate install-pre-commit;


.PHONY: delete-migrations
delete-migrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -not -path "*/.venv/*" -delete

.PHONY: import-user
import-user:
	poetry run python -m healthharmony.manage loaddata db.json

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

.PHONY: lint
lint:
	poetry run pre-commit run --all-files

.PHONY: install-pre-commit
install-pre-commit:
	poetry run pre-commit uninstall
	poetry run pre-commit install
