"""Experiment to train and evaluate various classifier models.

Notes
-----

The experiment can be launched with the following command::

PYTHONPATH=. luigi \
--module \
mle_challenge.experiments.explore_classifier_model.explore_classifier_model \
RunModelTrainEval \
--local-scheduler

"""

import os
import typing

import bentoml
import luigi
from luigi.util import requires
import pandas as pd
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

import mle_challenge
from mle_challenge.experiments.exploratory_data_analysis import (
    exploratory_data_analysis,
)

MODELS_PATH = f"{os.path.dirname(mle_challenge.__file__)}/../models/"


MAP_ROOM_TYPE = {
    "Shared room": 1,
    "Private room": 2,
    "Entire home/apt": 3,
    "Hotel room": 4,
}
MAP_NEIGHB = {
    "Bronx": 1,
    "Queens": 2,
    "Staten Island": 3,
    "Brooklyn": 4,
    "Manhattan": 5,
}


def _data_preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[:, "neighbourhood"] = df["neighbourhood"].map(MAP_NEIGHB)
    df.loc[:, "room_type"] = df["room_type"].map(MAP_ROOM_TYPE)
    return df


def training_pipeline(
        data: pd.DataFrame,
        n_estimators: int,
        training_seed: int,
        split_seed: int
) -> typing.Any:
    data = data.dropna(axis=0)
    processed_data = _data_preprocessing(data)

    feature_names = [
        "neighbourhood",
        "room_type",
        "accommodates",
        "bathrooms",
        "bedrooms",
    ]

    X = processed_data[feature_names] # pylint: disable=invalid-name
    y = processed_data["category"] # pylint: disable=invalid-name

    X_train, _, y_train, _ = train_test_split(  # pylint: disable=invalid-name
        X, y, test_size=0.15, random_state=split_seed
    )

    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=training_seed,
        class_weight="balanced",
        n_jobs=4,
    )
    clf.fit(X_train, y_train)

    return clf

def evaluation_pipeline(
        data: pd.DataFrame,
        clf: typing.Any,
        split_seed: int
) -> pd.DataFrame:
    data = data.dropna(axis=0)
    processed_data = _data_preprocessing(data)

    feature_names = [
        "neighbourhood",
        "room_type",
        "accommodates",
        "bathrooms",
        "bedrooms",
    ]

    indexes = list(range(len(processed_data)))

    X = processed_data[feature_names] # pylint: disable=invalid-name
    y = processed_data["category"] # pylint: disable=invalid-name

        # pylint: disable=invalid-name
    _, X_test, _, y_test, _, indexes_test = train_test_split(
        X, y, indexes, test_size=0.15, random_state=split_seed
    )

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)

    evaluation_df = pd.DataFrame(
        {
            "id": processed_data["id"].iloc[indexes_test],
            "price_category": y_test,
            "predicted_price_category": y_pred,
        }
    )

    price_category_cols = [
        f"price_category_prob_{x}" for x in range(y_proba.shape[1])
    ]
    evaluation_df[price_category_cols] = y_proba

    return evaluation_df


@requires(exploratory_data_analysis.PreprocessListingsData)
class TrainRandomForestClassifier(luigi.Task):
    """Pipeline task to train and validate a RandomForestClassifier."""
    model_name = luigi.parameter.Parameter()
    n_estimators = luigi.parameter.IntParameter()
    training_seed = luigi.parameter.IntParameter(default=0)
    split_seed = luigi.parameter.IntParameter(default=1)

    @property
    def output_path(self):
        return f"{MODELS_PATH}{self.model_name}_{self.n_estimators}.pkl"

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        preprocessed_listing = pd.read_csv(self.input().path)

        clf = training_pipeline(
            preprocessed_listing,
            self.n_estimators,
            self.training_seed,
            self.split_seed
        )

        with open(self.output_path, "wb") as f_hdl:
            pickle.dump(clf, f_hdl)


@requires(
    TrainRandomForestClassifier,
    exploratory_data_analysis.PreprocessListingsData
)
class EvaluateModel(luigi.Task):
    """Pipeline task to evaluate a trained RandomForestClassifier."""
    @property
    def output_path(self):
        return (
            f"{MODELS_PATH}{self.model_name}_"
            f"{self.n_estimators}_evaluation.csv"
        )

    def output(self):
        return luigi.LocalTarget(self.output_path)

    def run(self):
        with open(self.input()[0].path, "rb") as f_hdl:
            clf = pickle.load(f_hdl)

        preprocessed_listing = pd.read_csv(self.input()[1].path)

        evaluation_df = evaluation_pipeline(
            preprocessed_listing, clf, self.split_seed
        )

        evaluation_df.to_csv(self.output_path, index=False)


@requires(TrainRandomForestClassifier, EvaluateModel)
class RegisterModel(luigi.Task):
    """Pipeline task to register a model candidate on bentoml model registry."""
    @property
    def output_path(self):
        return (
            f"{MODELS_PATH}registered_{self.model_name}_"
            f"{self.n_estimators}_link"
        )

    def output(self):
        return luigi.LocalTarget(self.output_path)

    @staticmethod
    def symlink_force(target, link_name):
        try:
            os.symlink(target, link_name)
        except OSError:
            os.remove(link_name)
            os.symlink(target, link_name)

    def run(self):
        with open(self.input()[0].path, "rb") as f_hdl:
            clf = pickle.load(f_hdl)

        evaluation_df = pd.read_csv(self.input()[1].path)

        # Compute metrics to save as metadata
        y_test = evaluation_df["price_category"]
        y_pred = evaluation_df["predicted_price_category"]
        y_proba = evaluation_df[
            ["price_category_prob_0",
            "price_category_prob_1",
            "price_category_prob_2",
            "price_category_prob_3"
            ]
        ]

        model_name = f"{self.model_name}_{self.n_estimators}"
        saved_model = bentoml.sklearn.save_model(
            model_name,
            clf,
            metadata={
                "acc": accuracy_score(y_test, y_pred),
                "auc": roc_auc_score(y_test, y_proba, multi_class="ovr")
            },
        )
        self.symlink_force(saved_model.path, self.output_path)


class RunModelTrainEval(luigi.WrapperTask):
    def requires(self):
        for n_estimators in range(100, 550, 50):
            yield EvaluateModel(
                n_estimators=n_estimators,
                model_name="simple_classifier",
            )
        yield RegisterModel(
            n_estimators=500,
            model_name="simple_classifier",
        )
