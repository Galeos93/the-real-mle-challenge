"""Module with different functions for feature engineering."""

import pandas as pd
import numpy as np


def parse_num_bathrooms(text: str) -> float:
    try:
        if isinstance(text, str):
            bath_num = text.split(" ")[0]
            return float(bath_num)
        return np.nan
    except ValueError:
        return np.nan


def parse_price(price: pd.Series) -> pd.Series:
    price = price.map(lambda x: x if isinstance(x, str) else "")
    price = price.str.extract(r"(\d+).", expand=False)
    price = price.map(lambda x: x if pd.isnull(x) else int(x))
    return price


def create_category_field(df: pd.DataFrame) -> pd.DataFrame:
    df["category"] = pd.cut(
        df["price"], bins=[10, 90, 180, 400, np.inf], labels=[0, 1, 2, 3]
    )
    return df


def preprocess_amenities_column(df: pd.DataFrame) -> pd.DataFrame:
    df["TV"] = df["amenities"].str.contains("TV")
    df["TV"] = df["TV"].astype(int)

    df["Internet"] = df["amenities"].str.contains("Internet")
    df["Internet"] = df["Internet"].astype(int)

    df["Air_conditioning"] = df["amenities"].str.contains("Air conditioning")
    df["Air_conditioning"] = df["Air_conditioning"].astype(int)

    df["Kitchen"] = df["amenities"].str.contains("Kitchen")
    df["Kitchen"] = df["Kitchen"].astype(int)

    df["Heating"] = df["amenities"].str.contains("Heating")
    df["Heating"] = df["Heating"].astype(int)

    df["Wifi"] = df["amenities"].str.contains("Wifi")
    df["Wifi"] = df["Wifi"].astype(int)

    df["Elevator"] = df["amenities"].str.contains("Elevator")
    df["Elevator"] = df["Elevator"].astype(int)

    df["Breakfast"] = df["amenities"].str.contains("Breakfast")
    df["Breakfast"] = df["Breakfast"].astype(int)

    df.drop("amenities", axis=1, inplace=True)

    return df
