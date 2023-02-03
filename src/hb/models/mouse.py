from hb.models.record import Event


class ClickLeft(Event):
    pass


class ClickRight(Event):
    pass


class PressLeft(Event):
    pass


class PressRight(Event):
    pass


class PressMiddle(Event):
    pass


class ReleaseLeft(Event):
    pass


class ReleaseMiddle(Event):
    pass


class ReleaseRight(Event):
    pass


class Scroll(Event):
    value: int


class DoubleClick(Event):
    pass


class Move(Event):
    x: float
    y: float
