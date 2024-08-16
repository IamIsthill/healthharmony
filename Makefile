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
	make seed a=users
	make seed a=inventory &
	make seed a=treatment
	make import-user

.PHONY: test-doctor
test-doctor:
	poetry run python -m healthharmony.manage test healthharmony.doctor

.PHONY: test-inventory
test-inventory:
	poetry run python -m healthharmony.manage test healthharmony.inventory
