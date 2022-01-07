SHELL := /bin/bash
VENV=tut-env
XBLOCK=remoxblock

DOCKER_XBLOCK_PATH=/edx/app/edxapp/edx-platform/src
STUDIO=edx.devstack.studio
LMS=edx.devstack.lms

# This workflow is geared towards the docker devstack

default: ## default
	@echo default make rule invoked.

dump-env-vars:
	# TODO: is DEVSTACK_WORKSPACE needed anymore?
	# DEVSTACK_WORKSPACE needs to be in the environment!  and should
	# be the path to the parent directory of the devstack repo
	@echo ${DEVSTACK_WORKSPACE}

deploy-local-docker: | deploy-local-docker-lms deploy-local-docker-studio

deploy-local-docker-lms:
	docker exec -it $(LMS) mkdir -p $(DOCKER_XBLOCK_PATH)
	docker cp -a $(XBLOCK) $(LMS):$(DOCKER_XBLOCK_PATH)
	# why doesn't the following pip install into venv?
	# .. probably because docker exec doesn't init the venv.
	docker exec -it $(LMS) pip install $(DOCKER_XBLOCK_PATH)/$(XBLOCK)

deploy-local-docker-studio:
	docker exec -it $(STUDIO) mkdir -p $(DOCKER_XBLOCK_PATH)
	docker cp -a $(XBLOCK) $(STUDIO):$(DOCKER_XBLOCK_PATH)
	docker exec -it $(STUDIO) pip install $(DOCKER_XBLOCK_PATH)/$(XBLOCK)

clone-xblock-sdk:
	git clone "https://github.com/edx/xblock-sdk.git"

test: ## test
	echo test

clean: ## clean all the things
	echo implement clean makefile rule

work: ## open all files in editor
	emacs -nw Makefile 

install: ## install the xblock
	pip install -e $(XBLOCK)

run:
	python xblock-sdk/manage.py runserver

migrate:
	python xblock-sdk/manage.py migrate

log-workbench:
	tail -f var/workbench.log

kill-extra-containers:
	docker kill edx.devstack.forum
	docker kill edx.devstack.elasticsearch710


# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
	'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

FORCE:

