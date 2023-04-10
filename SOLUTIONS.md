# Project Set-up

First of all, you have to install `tox` virtual environment manager:

```bash
python -m pip install tox
```

After this, you can create your virtual environment with the dependencies established on
`requirements.txt`:

```bash
make env-create
```

And activate it:

```bash
source .tox/mle_challenge/bin/activate
```

# Challenge 1 - Refactor DEV code

To make the experimentation pipeline, I have used `luigi`. To execute a pipeline that
preprocesses the raw data, trains a series of models, evaluates them and sets a candidate on
a Model Registry, you simply have to execute the following command:

```bash
PYTHONPATH=. luigi --module mle_challenge.experiments.explore_classifier_model.explore_classifier_model RunModelTrainEval --local-scheduler
```

After launching it, you can see that the `RandomForestClassifier` with 500 `n_estimators`
was succesfully registered on BentoML's Model Registry by introducing the following command:

```bash
bentoml models list
```

Concretely, you will see a model with a tag like this: `simple_classifier_500:<hash>`.
Save the tag, since you will use it later.

# Challenge 2 - Build an API

To build the API, all you have to do is to create a "bento"
like the one found on `mle_challenge/bento`. Let's build it with this command,
using the model tag saved before:

```bash
MODEL_VERSION=<model_tag> make build-bento
```

You can see the bento was succesfully built and it is listed by executing this:

```bash
bentoml list
```

Note the bento's tag for later usage.

# Challenge 3 - Dockerize your solution

Once the bento is correctly built, dockerizing is simple. Use this command:

```bash
BENTO_TAG=<saved_bento_tag> make build-docker
```

You can check the image was correctly created by checking that it appears when executing
`docker images`.

Once built, you can use the following command to launch the docker locally:

```bash
MODEL_VERSION=<model_tag> PORT=3000 DOCKER_IMAGE=<docker image> make run-docker
```

Finally, you can check it works correctly by launching a query to the served model:

```python
import json
import requests

data = dict(
    id=39331263,
    accommodates=5,
    room_type="Entire home/apt",
    beds=2,
    bedrooms=2,
    bathrooms=1,
    neighbourhood="Brooklyn",
    tv=True,
    elevator=False,
    internet=False,
    latitude=40.65837,
    longitude=-73.98402,
)

response = requests.post(
    "http://0.0.0.0:3000/classify",
    headers={"content-type": "application/json"},
    data=json.dumps(data),
)

print(response.text)

```