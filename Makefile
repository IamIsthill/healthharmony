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
			poetry run python -m healthharmony.manage seed $(a) --number=$(n); \
		else \
			poetry run python -m healthharmony.manage seed $(a); \
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

.PHONY: dump
dump:
	poetry run python -m healthharmony.manage dumpdata>datas.json

.PHONY: test
test:
	if [ "$(a)" ]; then \
		poetry run python -m healthharmony.manage test healthharmony.$(a); \
	else \
		poetry run python -m healthharmony.manage test; \
	fi

.PHONY: install_lang
install_lang:
	poetry run python -m  healthharmony.install_lang

.PHONY: train_diagnosis
train_diagnosis:
	poetry run python -m healthharmony.manage train_diag_pred

.PHONY: poetry
poetry:
	pip install poetry
