ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
ENV_FILE_PATH?=
HOST_PORT?=3000

.PHONY: build
build:
	docker build . -t rickbot

.PHONY: run
run: build
	docker run -i --env-file ${ENV_FILE_PATH} -p ${HOST_PORT}:3000 -t "rickbot"
