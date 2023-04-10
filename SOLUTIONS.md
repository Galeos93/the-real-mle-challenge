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

All the code follows the `Continuous Integration` practice. Every commit pushed undergoes
linting check and testing using GitHub Actions (see `.github/workflows/ci_cd.yaml`).
The developers must execute `make lint` and `make test` commands before pushing to master.

# Challenge 1 - Refactor DEV code

## Usage

To make the experimentation pipeline, I have used `luigi`. To execute a pipeline that
preprocesses the raw data, trains a series of models, evaluates them and sets a candidate on
a Model Registry, you simply have to execute the following command:

```bash
PYTHONPATH=. luigi --module mle_challenge.experiments.explore_classifier_model.explore_classifier_model RunModelTrainEval --local-scheduler
```

After launching it, you can see that the `RandomForestClassifier` with 500 `n_estimators`
was successfully registered on BentoML's Model Registry by introducing the following command:

```bash
bentoml models list
```

Concretely, you will see a model with a tag like this: `simple_classifier_500:<hash>`.
Save the tag, since you will use it later.

## Discussion

When a data scientist creates an experiment that is composed of many phases
(data processing, model training), it can be challenging to replicate it,
especially if the experiment was done long ago. Moreover, the usage of Jupyter
Notebooks, where the code is often untested can make things even more complicated.

Using `luigi` as a framework to create an automated pipeline we meet the following
requirements:

- Traceability: for all the artifacts of an experiment (e.g., a trained model), it is known
what stages and parameters created them.
- Replicability: any user could launch an experiment and replicate the results obtained by another user.
- Maintainability: some pipeline stages (e.g., data filtering) can be used across different experiments.
Moreover, all the pieces can be tested.
- Readability: structuring the experiment on different stages helps on its understanding.
Moreover, `luigi` allows the creation of graphs to observe how the different stages are connected.

Once a model is trained, it can be saved on a Model registry. Having a Model Registry
allows us to have all models versioned and in a centralized place. For the Model Registry,
[`BentoML`](https://www.bentoml.com/) framework was used. `BentoML` is a mature software
that is widely used for the deployment stage of the MLOps paradigm.


# Challenge 2 - Build an API

## Usage

To build the API, all you have to do is to create a "bento"
like the one found on `mle_challenge/bento`. From the official website:

> Bento 🍱 is a file archive with all the source code, models, data files
> and dependency configurations required for running a user-defined bentoml.Service,
> packaged into a standardized format.


Let's build it with this command,
using the model tag saved before:

```bash
MODEL_VERSION=<model_tag> make build-bento
```

You can see the bento was successfully built and it is listed by executing this:

```bash
bentoml list
```

Note the bento's tag for later usage.

Some smoke tests were developed for testing the model service. To test it 
with a particular model version, you must execute the tests like this:

```bash
MODEL_VERSION=<model_tag>  make test
```

## Discussion

For serving the model via an API, `BentoML` framework was used.
It allows data scientists to define easily the model serving logic.
In addition, it provides useful features such as input validation and automatic API
documentation (see `docs/openapi.yaml`). For a simple model like the one obtained in this
challenge, `BentoML` is an excellent tool. Moreover, it couples perfectly with the
`BentoML` Model Registry used as part of the challenge.

# Challenge 3 - Dockerize your solution

## Usage

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

## Discussion

For the Docker creation, `BentoML` framework was used.
Creating a docker from a bento is extremely simple, especially for data scientists,
which may have never used tools such as `Docker` before.

