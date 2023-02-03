import logging
from threading import Thread

from pynput import mouse as py_mouse
from pynput.mouse import Button

from hb.core.listener import Listener
from hb.models.mouse import Move, PressLeft, ReleaseLeft, PressMiddle, ReleaseMiddle, PressRight, ReleaseRight, Scroll
from hb.models.record import Event

log = logging.getLogger(__name__)


class Mouse(Listener):

    def __init__(self, event_callback=None):
        self._recording: bool = False
        self._event_callback = event_callback
        self._listener = None
        self._listener_thread = None
        self._cx = 0
        self._cy = 0

    def on_event(self, evt: Event):
        if self._event_callback:
            self._event_callback(evt)

    def start(self):
        if self._recording: return
        self._recording = True
        log.info('Start recording mouse events')
        self._events = []
        self._listener = py_mouse.Listener(
            on_move=self.record_move,
            on_click=self.record_click,
            on_scroll=self.record_scroll)

        self._listener_thread = Thread(target=self._listener.start)
        self._listener_thread.daemon = True
        self._listener_thread.start()

    def record_move(self, x, y):
        pass
        # print('Pointer moved to {0}'.format(
        #    (x, y)))
        # self._events.append(Move(Position(x, y)))


    def record_click(self, x, y, button, pressed):
        print('{0} at {1}'.format('Pressed' if pressed else 'Released', (x, y)))
        if x!= self._cx or y!= self._cy:
            evt = Move(x=x, y=y)
            self.on_event(evt)
            self._cx = x
            self._cy = y
        if button == Button.left:
            if pressed:
                evt = PressLeft()
                self.on_event(evt)
            else:
                evt = ReleaseLeft()
                self.on_event(evt)
        elif button == Button.middle:
            if pressed:
                evt = PressMiddle()
                self.on_event(evt)

            else:
                evt = ReleaseMiddle()
                self.on_event(evt)

        elif button == Button.right:
            if pressed:
                evt = PressRight()
                self.on_event(evt)

            else:
                evt = ReleaseRight()
                self.on_event(evt)

    def record_scroll(self, x, y, dx, dy):
        print('Scrolled {0} at {1}'.format('down' if dy < 0 else 'up', (x, y)))
        self._events.append(Scroll(value=dy))

    def stop(self):
        if not self._recording: return
        if not self._listener: return
        self._listener.stop()
        self._listener_thread.join()
        self._recording = False
        log.info('Stop recording mouse events')

    def __str__(self):
        return 'mouse'
