env-create:
	tox -e mle_challenge

env-compile:
	pip-compile requirements.in

lint:
	pylint mle_challenge

test:
	pytest tests

build-bento:
	bentoml build -f ./mle_challenge/bento/bentofile.yaml mle_challenge/bento

build-docker:
	bentoml containerize ${BENTO_TAG}

run-docker:
	docker run -e MODEL_VERSION=${MODEL_VERSION} -it --rm -p ${PORT}:${PORT} ${DOCKER_IMAGE} serve --production