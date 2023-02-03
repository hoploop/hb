from datetime import datetime
from typing import List

from bson import ObjectId
from pydantic import Field, BaseModel

from hb.core.element import MongodbDocument, Element, datetime_default, uid_factory, list_factory
from hb.core.serialization import PyObjectId


def frame_default():
    return -1


class Event(BaseModel):
    ts: datetime = Field(default_factory=datetime_default)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Frame(BaseModel):
    number: int = Field(default=0)
    timestamp: datetime = Field(default_factory=datetime_default)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Scenario(MongodbDocument):
    application: PyObjectId
    name: str = Field(default_factory=uid_factory)
    description: str = Field(default='')
    events: List[Event] = Field(default_factory=list_factory)
    start: datetime = Field(default_factory=datetime_default)
    end: datetime = Field(default_factory=datetime_default)
    duration: float = Field(default=0.0)
    fps: int = Field(default=10)
    frames: List[Frame] = Field(default_factory=list_factory)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}
