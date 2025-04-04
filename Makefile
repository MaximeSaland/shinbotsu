pre_commit := $(shell which pre-commit)

# Get directory path for Makefile location. Used instead of PWD to allow usage of Makefile from another directories
MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

TESTS_DIR := $(MAKEFILE_DIR)/tests

install:
	pip install -r requirements.txt
	pip install -r requirements-devs.txt
	pre-commit install

## pre-commit tools ##
precommit-all:
	$(pre_commit) run --all-files

## docker tools ##
