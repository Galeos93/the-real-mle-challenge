import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier

from mle_challenge.experiments.explore_classifier_model import explore_classifier_model


@pytest.fixture()
def sample_dataset():
    df = pd.DataFrame(
        [
            [0, "Bronx", "Shared room", 4, 1, 1, "foo", 0],
            [1, "Queens", "Private room", 5, 1, 1, "bar", 3],
            [2, "Brooklyn", "Hotel room", 1, 0, 1, 1, 4],
        ],
        columns= [
            "id",
            "neighbourhood",
            "room_type",
            "accommodates",
            "bathrooms",
            "bedrooms",
            "others",
            "category"
        ]
    )
    return df


def test_training_pipeline(sample_dataset):
    model = explore_classifier_model.training_pipeline(sample_dataset, 10, 0, 0)
    assert model


def test_evaluation_pipeline(sample_dataset):
    mock_model = RandomForestClassifier(n_estimators=10)
    mock_model.fit(
        np.array([[1,1,1,1,1], [1,1,1,1,1], [1,1,1,1,1], [1,1,1,1,1]]),
        np.array([0, 1, 2, 3])
    )
    evaluation_df = explore_classifier_model.evaluation_pipeline(
        sample_dataset, mock_model, 0
    )
    expected_columns = [
        "id",
        "price_category",
        "predicted_price_category",
        "price_category_prob_0",
        "price_category_prob_1",
        "price_category_prob_2",
        "price_category_prob_3"
    ]
    assert list(evaluation_df.columns) == expected_columns
    np.testing.assert_almost_equal(
        len(evaluation_df),
        np.clip(np.round(len(sample_dataset)*0.1), 1, len(sample_dataset))
    )