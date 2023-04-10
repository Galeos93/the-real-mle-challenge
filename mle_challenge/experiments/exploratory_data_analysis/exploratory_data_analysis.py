"""Experiment where listings data from Airbnb is preprocessed."""

import luigi
from luigi.util import requires
import pandas as pd

from mle_challenge.experiments.exploratory_data_analysis import (
    feature_engineering
)


def preprocess_listings(df: pd.DataFrame) -> pd.DataFrame:
    df["bathrooms"] = df["bathrooms_text"].map(
        feature_engineering.parse_num_bathrooms
    )

    kept_columns = [
        "id",
        "neighbourhood_group_cleansed",
        "property_type",
        "room_type",
        "latitude",
        "longitude",
        "accommodates",
        "bathrooms",
        "bedrooms",
        "beds",
        "amenities",
        "price",
    ]
    df = df.loc[:, kept_columns]

    df.rename(
        columns={"neighbourhood_group_cleansed": "neighbourhood"}, inplace=True
    )

    df = df.dropna(axis=0)

    df["price"] = feature_engineering.parse_price(df["price"])
    df = df[df["price"] >= 10]

    df = feature_engineering.create_category_field(df)

    df = feature_engineering.preprocess_amenities_column(df)

    return df


class ListingsData(luigi.ExternalTask):
    @property
    def output_path(self):
        return (
            "/home/agarcia/repos/the-real-mle-challenge/data/raw/listings.csv"
        )

    def output(self):
        return luigi.LocalTarget(self.output_path)


@requires(ListingsData)
class PreprocessListingsData(luigi.Task):
    """Processes listings dataframe with `preprocess_listings` function."""
    @property
    def output_path(self):
        return (
            "/home/agarcia/repos/the-real-mle-challenge"
            "/data/processed/preprocessed_listings.csv"
        )

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        listings_df = pd.read_csv(self.input().path)
        preprocessed_listings = preprocess_listings(listings_df)
        preprocessed_listings.to_csv(self.output_path, index=True)


class RunFeatureEngineeringExperiment(luigi.WrapperTask):
    def requires(self):
        yield self.clone(PreprocessListingsData)
