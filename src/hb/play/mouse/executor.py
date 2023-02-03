
import pyautogui
import logging
from hb.core.executor import Executor

log = logging.getLogger(__name__)

class Mouse(Executor):

    def position(self) :
        """
        Returns the current mouse position
        :return: Position of the mouse
        """
        log.debug('Getting current mouse position')
        current_mouse_x, current_mouse_y = pyautogui.position()  # Get the XY position of the mouse
        return (current_mouse_x, current_mouse_y)

    def move(self, x: float,y:float):
        """
        Moves the mouse to a target position
        :param position: The position of the mouse to move to
        :return:
        """

        log.info('Moving mouse to position: {0},{1}'.format(x,y))
        pyautogui.moveTo(x, y)

    def scroll_vertical(self, value: float):
        """
        Scrolls the mouse vertically
        :param scroll: Negative values: scroll down, positive values scroll up
        :return:
        """
        pyautogui.scroll(value)  # scroll up 10 "clicks"

    def scroll_horizontal(self, value: float):
        """
        Scrolls the mouse horizontally
        :param scroll: Negative values: scroll down, positive values scroll up
        :return:
        """
        pyautogui.hscroll(value)  # scroll up 10 "clicks"

    def click(self):
        """
        Performs the mouse click
        :return:
        """
        log.debug('Clicking the mouse')
        pyautogui.click()

    def right_click(self):
        """
        Performs the mouse click
        :return:
        """
        log.debug('Clicking the mouse')
        pyautogui.rightClick()

    def doubleclick(self):
        """
        Performs the mouse doubleclick
        :return:
        """
        log.debug('Double clicking the mouse')
        pyautogui.doubleClick()