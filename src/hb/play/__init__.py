from datetime import datetime

from pydantic import Field

from hb.core.element import Element, datetime_default


class Action(Element):
    ts: datetime = Field(default_factory=datetime_default)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


