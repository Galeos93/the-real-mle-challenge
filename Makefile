env-create:
	tox -e mle_challenge

env-compile:
	pip-compile requirements.in

test:
	pytest tests