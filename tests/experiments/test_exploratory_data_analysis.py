import pytest
import numpy as np
import pandas as pd

from mle_challenge.experiments.exploratory_data_analysis import (
    exploratory_data_analysis,
    feature_engineering,
)


@pytest.mark.parametrize(
    "bathroom_text,expected_bathrooms",
    [
        ("1 bath", 1),
        ("2 baths", 2),
        ("2.0 baths", 2),
        ("10 private baths", 10),
        ("ten private baths", np.nan),
        (np.nan, np.nan),
        ("", np.nan),
    ],
)
def test_parse_num_bathrooms(bathroom_text, expected_bathrooms):
    bathrooms = feature_engineering.parse_num_bathrooms(bathroom_text)
    if np.isnan(expected_bathrooms):
        assert np.isnan(bathrooms)
    else:
        assert bathrooms == expected_bathrooms


@pytest.mark.parametrize(
    "price_text,expected_price",
    [
        (pd.Series(["$500.00", "$200.00", "$200.00"]), pd.Series([500, 200, 200])),
        (pd.Series(["", "$500.00"]), pd.Series([np.nan, 500])),
        (pd.Series(["500.00"]), pd.Series([500])),
        (pd.Series([np.nan]), pd.Series([np.nan])),
        (pd.Series([500]), pd.Series([np.nan])),
    ],
)
def test_parse_price(price_text, expected_price):
    price = feature_engineering.parse_price(price_text)
    pd.testing.assert_series_equal(price, expected_price)
