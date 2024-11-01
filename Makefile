.PHONY:run
run:
	poetry run python -m healthharmony.manage runserver

.PHONY: migrate
migrate:
	poetry run python -m healthharmony.manage makemigrations
	poetry run python -m healthharmony.manage migrate || poetry run python -m healthharmony.manage migrate account 0002_initial --fake; poetry run python -m healthharmony.manage migrate;

.PHONY: download
download:
	poetry run python -m healthharmony.manage dumpdata treatment inventory users > data.json

.PHONY: download-all
download-all:
	poetry run python -m healthharmony.manage dumpdata treatment > treatment.json
	poetry run python -m healthharmony.manage dumpdata inventory > inventory.json
	poetry run python -m healthharmony.manage dumpdata users > users.json

.PHONY: upload-all
upload-all:
	poetry run python -m healthharmony.manage loaddata users.json
	poetry run python -m healthharmony.manage loaddata inventory.json
	poetry run python -m healthharmony.manage loaddata treatment.json

.PHONY: upload
upload:
	poetry run python -m healthharmony.manage loaddata data.json


.PHONY: install
install:
	poetry install

.PHONY: update
update: install migrate install-pre-commit npm-install;


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
	poetry run pre-commit run

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

.PHONY: docker-build
docker-build:
	docker build -t healthharmony .
.PHONY: docker-run
docker-run:
	docker run --name app  -p 9000:9000  healthharmony

.PHONY: npm-install
npm-install:
	npm install

.PHONY: staff-test
staff-test:
	poetry run python -m healthharmony.staff.tests

.PHONY: flush
flush:
	poetry run python -m healthharmony.manage flush --noinput

.PHONY: sqlflush
sqlflush:
	poetry run python -m healthharmony.manage sqlflush

.PHONY: test-doctor
test-doctor:
	poetry run python -m healthharmony.manage test healthharmony.doctor

.PHONY: test-users
test-users:
	poetry run python -m healthharmony.manage test healthharmony.users

.PHONY: test-inventory
test-inventory:
	poetry run python -m healthharmony.manage test healthharmony.inventory

.PHONY: static
static:
	poetry run python -m healthharmony.manage collectstatic --noinput

.PHONY: deploy
deploy:
	poetry run daphne -p 80 -b 0.0.0.0 healthharmony.app.asgi:application

.PHONY: js
js:
	cd healthharmony/static/js

.PHONY: export
export:
	poetry run python -m healthharmony.manage dumpdata > temp.json

.PHONY: export-users
export-users:
	poetry run python -m healthharmony.manage dumpdata users > users.json

.PHONY: export-treatment
export-treatment:
	poetry run python -m healthharmony.manage dumpdata treatment > treatment.json

.PHONY: export-inventory
export-inventory:
	poetry run python -m healthharmony.manage dumpdata inventory > inventory.json

.PHONY: import
import:
	poetry run python -m healthharmony.manage loaddata users.json
	poetry run python -m healthharmony.manage loaddata treatment.json
