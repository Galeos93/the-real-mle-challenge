from enum import Enum
import os
from typing import Dict, Any

import bentoml
from bentoml.io import JSON
import pandas as pd
from pydantic import BaseModel, StrictBool, StrictInt, StrictFloat, Extra

MODEL_VERSION = os.environ.get("MODEL_VERSION")
SERVICE_NAME = os.environ.get("SERVICE_NAME", "prediction")


if MODEL_VERSION is not None:
    clf_runner = bentoml.sklearn.get(MODEL_VERSION).to_runner()
else:
    clf_runner = None

svc = bentoml.Service(
    SERVICE_NAME, runners=[clf_runner] if clf_runner is not None else None
)


class RoomType(str, Enum):
    shared_room = "Shared room"
    private_room = "Private room"
    entire_home = "Entire home/apt"
    hotel_room = "Hotel room"


class NeighbourhoodType(str, Enum):
    bronx = "Bronx"
    queens = "Queens"
    staten_island = "Staten Island"
    brooklyn = "Brooklyn"
    manhattan = "Manhattan"


MAP_ROOM_TYPE = {
    RoomType.shared_room.value: 1,
    RoomType.private_room.value: 2,
    RoomType.entire_home.value: 3,
    RoomType.hotel_room.value: 4,
}


MAP_NEIGHB = {
    NeighbourhoodType.bronx.value: 1,
    NeighbourhoodType.queens.value: 2,
    NeighbourhoodType.staten_island.value: 3,
    NeighbourhoodType.brooklyn.value: 4,
    NeighbourhoodType.manhattan.value: 5,
}


class PropertyFeatures(BaseModel):
    id: StrictInt
    accommodates: StrictInt
    room_type: RoomType
    beds: StrictInt
    bedrooms: StrictInt
    bathrooms: StrictInt
    neighbourhood: NeighbourhoodType
    tv: StrictBool
    elevator: StrictBool
    internet: StrictBool
    latitude: float
    longitude: float

    class Config:
        extra = Extra.forbid


@svc.api(
    input=JSON(pydantic_model=PropertyFeatures),
    output=JSON(),
)
def classify(input_data: PropertyFeatures) -> Dict[str, Any]:
    # TODO: logging
    print(input_data)
    input_df = pd.DataFrame([input_data.dict()])

    id = input_df["id"].to_list()[0]

    input_df = input_df[
        ["neighbourhood", "room_type", "accommodates", "bathrooms", "bedrooms"]
    ]
    input_df["neighbourhood"] = input_df["neighbourhood"].map(MAP_NEIGHB)
    input_df["room_type"] = input_df["room_type"].map(MAP_ROOM_TYPE)

    result = clf_runner.predict.run(input_df)[0]
    return {"id": id, "price_category": result}