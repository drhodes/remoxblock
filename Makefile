SHELL := /bin/bash
VENV=tut-env
XBLOCK=remoxblock

DOCKER_XBLOCK_PATH=/edx/app/edxapp/edx-platform/src
STUDIO=edx.devstack.studio
LMS=edx.devstack.lms

PIP=/edx/app/edxapp/venvs/edxapp/bin/pip

# This workflow is geared towards the dockerized devstack

default: ## default
	@echo default make rule invoked.

dump-env-vars:
	# DEVSTACK_WORKSPACE needs to be in the host environment, and
	# should be the path to the parent directory of the devstack repo
	# 
	@echo ${DEVSTACK_WORKSPACE}

deploy-local-docker: deploy-local-docker-lms deploy-local-docker-studio

deploy-local-docker-lms:
	docker cp -a $(XBLOCK) $(LMS):$(DOCKER_XBLOCK_PATH)
	docker exec -it $(LMS) $(DOCKER_XBLOCK_PATH)/$(XBLOCK)/_install.bash
	cd ${DEVSTACK_WORKSPACE}/devstack && $(MAKE) lms-restart

deploy-local-docker-studio:
	docker cp -a $(XBLOCK) $(STUDIO):$(DOCKER_XBLOCK_PATH)
	docker exec -it $(STUDIO) $(DOCKER_XBLOCK_PATH)/$(XBLOCK)/_install.bash
	cd ${DEVSTACK_WORKSPACE}/devstack && $(MAKE) studio-restart

clone-xblock-sdk:
	git clone "https://github.com/edx/xblock-sdk.git"

test: ## test
	pytest tests/test_answer_set.py

clean: ## clean all the things
	echo implement clean makefile rule

work: ## open all files in editor
	emacs -nw Makefile 

install: ## install the xblock
	pip install -e $(XBLOCK)

kill-extra-containers: ## when memory is tight.
	docker kill edx.devstack.credentials             || true
	docker kill edx.devstack.discovery               || true
	docker kill edx.devstack.ecommerce               || true
	docker kill edx.devstack.edxnotesapi             || true
	docker kill edx.devstack.elasticsearch710        || true
	docker kill edx.devstack.forum                   || true
	docker kill edx.devstack.frontend-app-payment    || true
	docker kill edx.devstack.lms_watcher             || true
	docker kill edx.devstack.studio_watcher          || true

kill-extra-containers2:
	docker kill edx.devstack.ecommerce               || true
	docker kill edx.devstack.elasticsearch710        || true
	docker kill edx.devstack.forum                   || true
	docker kill edx.devstack.frontend-app-payment    || true



# Workbench rules -------------------------------------------------------

workbench-run:
	python xblock-sdk/manage.py runserver

workbench-migrate:
	python xblock-sdk/manage.py migrate

workbench-log:
	tail -f var/workbench.log


# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
	'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

FORCE:



