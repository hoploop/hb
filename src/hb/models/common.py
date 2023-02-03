from typing import List

from bson import ObjectId
from pydantic import Field, BaseModel

from hb.api.config import list_default
from hb.core.element import MongodbDocument
from hb.core.serialization import PyObjectId
from hb.models.record import Scenario


class Application(MongodbDocument):
    name: str
    description: str = Field(default='')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ApplicationScenarios(BaseModel):
    application: PyObjectId
    total: int = Field(default=0)
    scenarios: List[Scenario] = Field(default_factory=list_default)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}


class Applications(BaseModel):
    total: int
    applications: List[Application]

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str, PyObjectId: str}
