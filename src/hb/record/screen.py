import logging
import os
import time
from datetime import datetime
from threading import Thread

import cv2
import numpy as np
import pyautogui as pyautogui

from pydantic import BaseModel, Field

from hb.core.listener import Listener
from hb.models.record import Frame

log = logging.getLogger(__name__)


class Config(BaseModel):
    fps: int = Field(default=10)


    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class Screen(Listener):

    def __init__(self,folder:str,fps:int,on_frame=None,on_start=None,on_end=None):
        self._folder = folder
        self._on_start = on_start
        self._on_end = on_end
        self._on_frame = on_frame
        self._fps = fps
        self._recording = False
        self._filename = None
        self._current = None
        self._current_img = None
        self._listener = None
        self._recorder = None

    def size(self):
        """
        Gets the primary screen size
        :return:
        """
        log.debug('Getting the primary screen size')
        screen_width, screen_height = pyautogui.size()
        return (screen_width, screen_height)


    def start(self):
        if self._recording: return
        self._recording = True
        self._listener = Thread(target=self.listener_loop)
        self._recorder = Thread(target=self.record_loop)
        self._listener.daemon = True
        self._recorder.daemon = True
        self._listener.start()
        self._recorder.start()

    def listener_loop(self):
        while self._recording:
            try:
                self._current = pyautogui.screenshot()
                self._current_img = cv2.cvtColor(np.array(self._current), cv2.COLOR_RGB2BGR)
            except KeyboardInterrupt:
                break

    def record_loop(self):
        output = os.path.join(self._folder,"video.avi")
        buffer = []
        self._current = pyautogui.screenshot()
        img = cv2.cvtColor(np.array(self._current), cv2.COLOR_RGB2BGR)
        self._current_img = img
        # get info from img
        height, width, channels = img.shape
        if self._on_start:
            self._on_start(datetime.utcnow())
        while self._recording:
            try:
                buffer.append(self._current_img)
                if self._on_frame:
                    self._on_frame(Frame(number=len(buffer)-1,timestamp=datetime.utcnow()))
                time.sleep(1 / self._fps)
            except KeyboardInterrupt:
                break
        if self._on_end:
            self._on_end(datetime.utcnow())
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output, fourcc, self._fps, (width, height))

        # Write the frames to the file
        for frame in buffer:
            out.write(frame)
        out.release()


    def stop(self):
        if not self._recording: return
        self._recording = False
        self._recorder.join()
        self._listener.join()

    def region_screenshot(self, x, y, w, h):
        """
        Performa a screenshot of a specific region of the
        screen
        :return:
        """
        im = pyautogui.screenshot(region=(x, y, w, h))
        # pic = Picture(region._w, region._h, im)

    def __str__(self):
        return 'screen'
