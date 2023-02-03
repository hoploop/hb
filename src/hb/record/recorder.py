import json
import logging
import os.path
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from pydantic import BaseModel, Field

from hb.core.element import ElementEncoder
from hb.models.record import Event, Frame, Scenario
from hb.record.keyboard import Keyboard
from hb.record.mouse import Mouse
from hb.record.screen import Screen

log = logging.getLogger(__name__)


class Config(BaseModel):
    folder: str = Field(default='recordings')

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Recorder:

    def __init__(self, config: Config = None):
        self.config = config
        if self.config is None:
            self.config = Config()
        self.setup()

    def setup(self):
        fpath = os.path.join(os.getcwd(), self.config.folder)
        if not os.path.exists(fpath):
            os.mkdir(fpath)

    def on_event(self, evt: Event):
        self.scenario.events.append(evt)

    def on_frame(self, frame: Frame):
        self.scenario.frames.append(frame)

    def on_start(self, ts):
        self.scenario.start = ts

    def on_end(self, ts):
        self.scenario.end = ts

    def start(self):
        self.scenario = Scenario()
        fpath = os.path.join(os.getcwd(), self.config.folder)
        fpath = os.path.join(fpath, self.scenario.name)
        os.mkdir(fpath)
        self.keyboard = Keyboard(event_callback=self.on_event)
        self.mouse = Mouse(event_callback=self.on_event)
        self.screen = Screen(fpath, self.scenario.fps, self.on_frame, self.on_start, self.on_end)
        self.screen.start()
        self.mouse.start()
        time.sleep(1)
        self.keyboard.start()

    def stop(self):
        print('Stopping mouse')
        self.mouse.stop()
        print('Stopping keyboard')
        self.keyboard.stop()
        print('Stopping screen')
        self.screen.stop()
        fpath = os.path.join(os.getcwd(), self.config.folder)
        fpath = os.path.join(fpath, self.scenario.name)
        duration = self.scenario.end - self.scenario.start
        self.scenario.duration = duration.total_seconds()
        log.debug('Saving scenario: {0}'.format(self.scenario.name))
        with open(os.path.join(fpath, 'events.json'), 'w') as f:
            json.dump(self.scenario.dict(by_alias=True), f, cls=ElementEncoder)

