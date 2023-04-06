env-create:
	tox -e mle_challenge

env-compile:
	pip-compile requirements.in

lint:
	pylint mle_challenge

test:
	pytest tests