import os
import time

import json
import requests
import subprocess

import pytest

from mle_challenge.bento.service import PriceCategory


@pytest.fixture()
def valid_data():
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
    return data


@pytest.fixture(scope="module")
def bentoml_server():
    process = subprocess.Popen(
        ["bentoml", "serve", "mle_challenge.bento.service"],
        env=os.environ,
        stdout=subprocess.PIPE,
    )
    retries = 5
    while retries > 0:
        try:
            _ = requests.get("http://0.0.0.0:3000/livez", verify=False)
            break
        except Exception:
            time.sleep(1)
            retries -= 1

        if not retries:
            raise RuntimeError("Failed to start server")

    yield process
    process.terminate()
    process.wait()


@pytest.mark.skipif(
    os.environ.get("MODEL_VERSION", None) is None,
    reason="MODEL_VERSION env variable must be set",
)
def test_valid_input(bentoml_server, valid_data):
    expected_output = {
        "id": 39331263,
        "price_category": PriceCategory.high.value
    }

    response = requests.post(
        "http://0.0.0.0:3000/classify",
        headers={"content-type": "application/json"},
        data=json.dumps(valid_data),
    )
    assert response.status_code == 200

    assert expected_output == json.loads(response.text)


@pytest.mark.skipif(
    os.environ.get("MODEL_VERSION", None) is None,
    reason="MODEL_VERSION env variable must be set",
)
@pytest.mark.parametrize(
    "invalid_fields",
    [
        dict(id="1"),
        dict(room_type=1),
        dict(neighbourhood=1),
        dict(neighbourhood="Unknown"),
        dict(room_type="Unknown"),
        dict(new_value=0),
        dict(beds="1"),
        dict(bedrooms="1"),
        dict(bathrooms="1"),
        dict(accomodates="1"),
        dict(elevator=0),
        dict(elevator="False"),
        dict(internet=0),
        dict(internet="False"),
        dict(tv=0),
        dict(tv="False"),
        dict(latitude="100º"),
        dict(longitude="100º"),
    ],
)
def test_invalid_input(valid_data, invalid_fields):
    valid_data.update(**invalid_fields)
    response = requests.post(
        "http://0.0.0.0:3000/classify",
        headers={"content-type": "application/json"},
        data=json.dumps(valid_data),
    )
    assert response.status_code == 400
    assert "Invalid JSON" in response.text
