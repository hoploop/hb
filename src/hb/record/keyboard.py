import logging
from threading import Thread

from pynput import keyboard as py_keyboard

from hb.core.listener import Listener
from hb.models.keyboard import Press, Release
from hb.models.record import Event

log = logging.getLogger(__name__)


class Keyboard(Listener):

    def __init__(self, event_callback=None):
        self._event_callback = event_callback
        self._recording: bool = False
        self._listener = None
        self._listener_thread = None

    def __str__(self):
        return 'keyboard'

    def on_event(self, evt: Event):
        if self._event_callback:
            self._event_callback(evt)

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(
                key.char))
            evt = Press(key=str(key.char))
            self.on_event(evt)

        except AttributeError:
            print('special key {0} pressed'.format(
                key))
            evt = Press(key=str(key))
            self.on_event(evt)

    def on_release(self, key):
        print('{0} released'.format(
            key))
        try:
            print('alphanumeric key {0} released'.format(
                key.char))
            evt = Release(key=str(key.char))
            self.on_event(evt)

        except AttributeError:
            print('special key {0} released'.format(
                key))
            evt = Release(key=str(key))
            self.on_event(evt)

    def start(self):
        if self._recording: return
        log.info('Start recording keyboard events')
        self._recording = True
        self._listener = py_keyboard.Listener(on_press=self.on_press,
                                              on_release=self.on_release)
        self._listener_thread = Thread(target=self._listener.start)
        self._listener_thread.daemon = True
        self._listener_thread.start()

    def stop(self):
        if not self._recording: return
        if not self._listener: return

        self._listener.stop()
        self._listener_thread.join()
        self._recording = False
        log.info('Stop recording keyboard events')
