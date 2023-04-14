ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif

VENV = .venv
ifeq ($(OS),Windows_NT)
    PYTHON_EXECUTABLE = python
    VENV_BIN = $(VENV)/Scripts
else
    PYTHON_EXECUTABLE = python3.11
    VENV_BIN = $(VENV)/bin
endif

POETRY_VERSION=1.2
POETRY_RUN = $(VENV_BIN)/poetry run

# Manually define main variables

APPLICATION_NAME = tg_cipher_bot

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

TEST = $(POETRY_RUN) pytest --verbosity=2 --showlocals --log-level=DEBUG
CODE = bot tools tests

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

# Commands

.PHONY: help
help: ##@Help Show this help
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)


.PHONY: env
env:  ##@Environment Create .env file with variables
	@$(eval SHELL:=/bin/bash)
	@cp .env.example .env


.PHONY: venv
venv: ##@Environment Create virtual environment, no need in docker
	$(PYTHON_EXECUTABLE) -m venv $(VENV)
	$(VENV_BIN)/python -m pip install --upgrade pip
	$(VENV_BIN)/python -m pip install poetry==$(POETRY_VERSION)
	$(VENV_BIN)/poetry config virtualenvs.create true
	$(VENV_BIN)/poetry config virtualenvs.in-project true


.PHONY: install
install: ##@Code Install dependencies
	$(VENV_BIN)/poetry install --no-interaction --no-ansi


.PHONY: install-prod
install-prod: ##@Code Install dependencies for production only
	$(VENV_BIN)/poetry install --without dev --no-interaction --no-ansi


.PHONY: poetry-add
poetry-add: ##@Code Add new dependency
	$(VENV_BIN)/poetry add $(args)


.PHONY: up
up: ##@Application Up Bot
	$(POETRY_RUN) python -m bot


.PHONY: up-scheduler
up-scheduler: ##@Application Up Scheduler
	$(POETRY_RUN) python -m bot.scheduler

.PHONY: migrate
migrate:  ##@Database Do all migrations in database
	$(POETRY_RUN) alembic upgrade $(args)

.PHONY: revision
revision:  ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
	$(POETRY_RUN) alembic revision --autogenerate

.PHONY: downgrade
downgrade:  ##@Database Downgrade migration on one revision
	alembic downgrade -1

.PHONY: db
db: ##@Database Docker up db
	docker-compose up -d postgres

.PHONY: test
test: ##@Testing Runs pytest with coverage
	$(TEST) $(args) --cov

.PHONY: test-fast
test-fast: ##@Testing Runs pytest with exitfirst
	$(TEST) --exitfirst

.PHONY: test-failed
test-failed: ##@Testing Runs pytest from last-failed
	$(TEST) --last-failed

.PHONY: test-cov
test-cov: ##@Testing Runs pytest with coverage report
	$(TEST) --cov --cov-report html

.PHONY: test-mp
test-mp: ##@Testing Runs pytest with multiprocessing
	$(TEST) --cov -n auto

.PHONY: test-fast-mp
test-fast-mp: ##@Testing Runs pytest with exitfirst with multiprocessing
	$(TEST) --exitfirst -n auto

.PHONY: test-failed-mp
test-failed-mp: ##@Testing Runs pytest from last-failed with multiprocessing
	$(TEST) --last-failed -n auto

.PHONY: test-cov-mp
test-cov-mp: ##@Testing Runs pytest with coverage report with multiprocessing
	$(TEST) --cov --cov-report html -n auto

.PHONY: format
format: ###@Code Formats all files
	$(POETRY_RUN) autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(POETRY_RUN) isort $(CODE)
	$(POETRY_RUN) black --line-length 79 --target-version py311 --skip-string-normalization $(CODE)
	$(POETRY_RUN) unify --in-place --recursive $(CODE)

.PHONY: lint
lint: ###@Code Lint code
	$(POETRY_RUN) flake8 --jobs 4 --statistics --show-source $(CODE)
	$(POETRY_RUN) pylint $(CODE)
	$(POETRY_RUN) mypy $(CODE)
	$(POETRY_RUN) black --line-length 79 --target-version py311 --skip-string-normalization --check $(CODE)
	$(POETRY_RUN) pytest --dead-fixtures --dup-fixtures
	$(POETRY_RUN) safety check --full-report || echo "Safety check failed"

.PHONY: check
check: gen format lint test-mp ###@Code Format and lint code then run tests

.PHONY: docker-up
docker-up: ##@Application Docker up
	docker-compose up --remove-orphans

.PHONY: docker-up-d
docker-up-d: ##@Application Docker up detach
	docker-compose up -d --remove-orphans
	docker-compose up -d --force-recreate nginx

.PHONY: docker-build
docker-build: ##@Application Docker build
	docker-compose build

.PHONY: docker-up-build
docker-up-build: ##@Application Docker up detach with build
	docker-compose up -d --build --remove-orphans

.PHONY: docker-down
docker-down: ##@Application Docker down
	docker-compose down

.PHONY: docker-stop
docker-stop: ##@Application Docker stop some app
	docker-compose stop $(args)

.PHONY: docker-clean
docker-clean: ##@Application Docker prune -f
	docker image prune -f

.PHONY: docker
docker: docker-clean docker-build docker-up-d docker-clean ##@Application Docker prune, up, run and prune

.PHONY: open
open: ##@Docker Open container in docker
	docker exec -it $(args) /bin/bash

.PHONY: docker-run
docker-run: ##@Docker Run sh in paused docker container
	docker run --rm -it --entrypoint bash $(args)


.PHONY: docker-migrate
docker-migrate: ##@Application Migrate db in docker
	docker exec $(APPLICATION_NAME) make migrate $(args)

.PHONY: commit
commit: gen format lint ##@Git Commit with message all files (with lint)
	$(eval MESSAGE := $(shell read -p "Commit message: " MESSAGE; echo $$MESSAGE))
	@git add .
	@git status
	@git commit -m "$(MESSAGE)"

.PHONY: commit-fast
commit-fast: format ##@Git Commit with message all files (no lint)
	$(eval MESSAGE := $(shell read -p "Commit message: " MESSAGE; echo $$MESSAGE))
	@git add .
	@git status
	@git commit -m "$(MESSAGE)"

.PHONY: push
push: ##@Git Push to origin
	@git push

.PHONY: pull
pull: ##@Git Pull from origin
	@git pull

.PHONY: check-git
git: check commit ##@Git Check and commit

.PHONY: update
update: pull dump-local docker-build ##@Application Update docker app
	@make docker-down
	@make delete-container-data
	@make docker
	@make docker-migrate head

.PHONY: update-server
update-server: ##@Application Update docker app on server
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	ssh -p $(PORT) $(USERNAME)@$(HOST) "cd tg_cipher_bot; git pull && make update; exit;"
	@echo "Server updated"

.PHONY: dump
dump: ##@Database Dump database from server
	$(eval FILENAME=backup_$(shell date +%Y%m%d_%H%M%S).sql)
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	$(eval DB_NAME=$(shell cat deploy/db_name.txt))
	$(eval DB_USERNAME=$(shell cat deploy/db_username.txt))

	echo "Dumping database to $(FILENAME)"
	ssh -p $(PORT) $(USERNAME)@$(HOST) "docker exec postgres_container pg_dump -f $(FILENAME) -d $(DB_NAME) -U $(DB_USERNAME);docker cp postgres_container:$(FILENAME) $(FILENAME);docker exec postgres_container rm $(FILENAME);exit;"
	scp -P $(PORT) $(USERNAME)@$(HOST):$(FILENAME) db/$(FILENAME)
	ssh -p $(PORT) $(USERNAME)@$(HOST) "rm $(FILENAME); exit;"
	echo "Done"

.PHONY: dump-local
dump-local: ##@Database Dump database local
	$(eval FILENAME=backup_$(shell date +%Y%m%d_%H%M%S).sql)

	echo "Dumping database to $(FILENAME)"
	docker exec postgres_container pg_dump -f $(FILENAME) -d $(POSTGRES_DB) -U $(POSTGRES_USER)
	docker cp postgres_container:$(FILENAME) db/$(FILENAME)
	docker exec postgres_container rm $(FILENAME)
	echo "Done"

.PHONY: restore-local
restore-local: ##@Database Restore database local
	exit 1;
	$(eval FILENAME=$(args))
	$(eval DB_NAME=$(shell cat deploy/db_name.txt))
	$(eval DB_USERNAME=$(shell cat deploy/db_username.txt))

	echo "Restoring local database from $(FILENAME)"
	docker cp db/$(FILENAME) postgres_container:$(FILENAME)
	docker exec postgres_container psql -d $(DB_NAME) -U $(DB_USERNAME) -f $(FILENAME)
	docker exec postgres_container rm $(FILENAME)
	echo "Done"

.PHONY: restore-server
restore-server: ##@Database Restore database on server
	exit 1;
	$(eval FILENAME=$(args))
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	$(eval DB_NAME=$(shell cat deploy/db_name.txt))
	$(eval DB_USERNAME=$(shell cat deploy/db_username.txt))

	echo "Restoring database from $(FILENAME)"
	scp -P $(PORT) db/$(FILENAME) $(USERNAME)@$(HOST):$(FILENAME)
	ssh -p $(PORT) $(USERNAME)@$(HOST) "docker cp $(FILENAME) postgres_container:$(FILENAME); docker exec postgres_container psql -d $(DB_NAME) -U $(DB_USERNAME) -f (FILENAME); docker exec postgres_container rm $(FILENAME); rm (FILENAME); exit;"
	echo "Done"

.PHONY: file-copy
file-copy: ##@File Copy file from server
	$(eval FILENAME=$(args))
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))

	echo "Copying file $(FILENAME) from server"
	scp -P $(PORT) $(USERNAME)@$(HOST):$(FILENAME) $(FILENAME)
	echo "Done"

.PHONY: connect
connect: ##@Server Connect to server
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	ssh -p $(PORT) $(USERNAME)@$(HOST)

.PHONY: docker-clear-logs
docker-clear-logs: ##@Application Clear logs
	sudo sh -c "truncate -s 0 /var/lib/docker/containers/**/*-json.log"

.PHONY: docker-logs-size
docker-logs-size: ##@Application Get logs size
	sudo sh -c "du -ch /var/lib/docker/containers/*/*-json.log | grep total"

.PHONY: show-used-space
show-used-space: ##@Ubuntu Show used space on disk
	du / -aBM 2>/dev/null | sort -nr | head -n 50 | more

.PHONY: show-space
show-space: ##@Ubuntu Show space on disk
	df -h

.PHONY: clear-tmp
clear-tmp: ##@Ubuntu Clear tmp
	sudo find /tmp -type f -atime +10 -delete

.PHONY: get-scheduler-logs
get-scheduler-logs: ##@Application Get scheduler logs
	$(eval FILENAME=scheduler_logs_$(shell date +%Y%m%d_%H%M%S).log)
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	$(eval DB_NAME=$(shell cat deploy/db_name.txt))
	$(eval DB_USERNAME=$(shell cat deploy/db_username.txt))

	echo "Get scheduler logs to $(FILENAME)"
	ssh -p $(PORT) $(USERNAME)@$(HOST) "docker logs scheduler >& /tmp/$(FILENAME);exit;"
	scp -P $(PORT) $(USERNAME)@$(HOST):/tmp/$(FILENAME) logs/$(FILENAME)
	ssh -p $(PORT) $(USERNAME)@$(HOST) "rm /tmp/$(FILENAME); exit;"
	echo "Done"

.PHONY: run-job
run-job: docker-build ##@Application Run scheduler job in docker
	docker-compose run --rm --entrypoint make scheduler run-job-local $(args)

.PHONY: run-job-local
run-job-local: ##@Application Run scheduler job local
	$(eval JOB_NAME=$(args))
	$(VENV_BIN)/python -m tools runjob $(JOB_NAME)

.PHONY: add-ssh-key-to-server
add-ssh-key-to-server: ##@Server Add ssh key to server
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))

	echo "Add ssh key to server"
	ssh-copy-id -i ~/.ssh/id_rsa.pub -p $(PORT) $(USERNAME)@$(HOST)
	echo "Done"

.PHOMY: generate-deploy-key
generate-deploy-key: ##@Deploy Generate deploy key
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))

	([ ! -e deploy/id_rsa ] && echo "Generating deploy key") || (echo "Deploy key already exists, remove deploy/id_rsa to generate new one" && exit 1)
	ssh-keygen -t rsa -b 4096 -C "$(USERNAME)@$(HOST)" -q -N "" -f deploy/id_rsa
	ssh-copy-id -i deploy/id_rsa.pub -p $(PORT) $(USERNAME)@$(HOST)

.PHONY: gen
gen: ##@Application Generate files
	$(VENV_BIN)/python -m tools gen $(args)
	@make format

.PHONY: sqlalchemy
sqlalchemy: ##@Application Open sqlalchemy shell
	$(VENV_BIN)/python -m tools sqlalchemy $(args)

.PHONY: hash-password
hash-password: ##@Application Hash password
	$(VENV_BIN)/python -m tools hash-password $(args)

.PHONY: vpn-install
vpn-install: ##@VPN Install VPN
	sudo apt install apt-transport-https
	sudo wget https://swupdate.openvpn.net/repos/openvpn-repo-pkg-key.pub
	sudo apt-key add openvpn-repo-pkg-key.pub
	sudo wget -O /etc/apt/sources.list.d/openvpn3.list https://swupdate.openvpn.net/community/openvpn3/repos/openvpn3-$(lsb_release -s -c).list
	sudo apt update
	sudo apt install openvpn3 -y

.PHONY: vpn-start
vpn-start: ##@VPN Start VPN
	openvpn3 session-start --config deploy/vpn.ovpn

.PHONY: vpn-stop
vpn-stop: ##@VPN Stop VPN
	sudo killall openvpn3

.PHONY: docker-save-elk
docker-save-elk: ##@Docker SAVE ELK images
	docker save -o logs/elasticsearch.docker docker.elastic.co/elasticsearch/elasticsearch:8.5.3
	docker save -o logs/logstash.docker docker.elastic.co/logstash/logstash:8.5.3
	docker save -o logs/kibana.docker docker.elastic.co/kibana/kibana:8.5.3

.PHONY: docker-load-elk
docker-load-elk: ##@Docker LOAD ELK images
	docker load -i logs/elasticsearch.docker
	docker load -i logs/logstash.docker
	docker load -i logs/kibana.docker

.PHONY: server-copy
server-copy: ##@Server Copy files to server
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	$(eval FILES=$(args))

	echo "Copy files to server"
	scp -P $(PORT) $(FILES) $(USERNAME)@$(HOST):/tmp
	echo "Done"

.PHONY: server-copy-elk
server-copy-elk: ##@Server Copy ELK images to server
	@make server-copy args="logs/elasticsearch.docker logs/logstash.docker logs/kibana.docker"

.PHONY: update-dev-branch
update-dev-branch: ##@Git Rebase dev on main branch
	@git checkout main
	@git pull
	@git checkout dev
	@git rebase main

.PHONY: delete-container-data
delete-container-data: ##@Docker Prune containers
	docker container prune -f

.PHONY: ssh-tunnel
ssh-tunnel: ##@Server SSH tunnel to server for grafana
	$(eval PORT=$(shell cat deploy/port.txt))
	$(eval HOST=$(shell cat deploy/host.txt))
	$(eval USERNAME=$(shell cat deploy/username.txt))
	ssh -p $(PORT) -L 3000:127.0.0.1:3000 -C -N $(USERNAME)@$(HOST)

%::
	echo $(MESSAGE)
