from unittest import mock

import pytest

from mle_challenge.bento import service


@pytest.fixture()
def mock_runner():
    run_method_output = [0]

    runner = mock.MagicMock()
    runner.predict.run = mock.MagicMock(return_value=run_method_output)

    return runner


@pytest.fixture()
def valid_input_model():
    return service.PropertyFeatures(
        id=100,
        accommodates=1,
        room_type="Shared room",
        beds=1,
        bedrooms=1,
        bathrooms=1,
        neighbourhood="Bronx",
        tv=False,
        elevator=False,
        internet=False,
        latitude=1000,
        longitude=-1000,
    )


class TestService:
    @staticmethod
    def test_given_valid_input_and_model_output_prediction_is_returned(
        valid_input_model, monkeypatch, mock_runner
    ):
        monkeypatch.setattr(
            service,
            "clf_runner",
            mock_runner,
        )
        output = service.svc.apis["classify"].func(input_data=valid_input_model)
        assert isinstance(output, dict)
