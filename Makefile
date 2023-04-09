env-create:
	tox -e mle_challenge

env-compile:
	pip-compile requirements.in

lint:
	pylint mle_challenge

test:
	pytest tests

build-bento:
	bentoml build $(WHATEVER)

build-docker:
	bentoml containerize $(CONTAINER_NAME)