from bson import ObjectId

from hb.core.element import MongodbDocument


class YoloLabel(MongodbDocument):
    application: str
    scenario: str
    frame: int
    x: float
    y: float
    w: float
    h: float
    name: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
