import pyautogui

from hb.core.executor import Executor


class Keyboard(Executor):


    def press_and_release(self, key: str):
        """
        Press a key (key down and up
        """
        pyautogui.press(key)

    def write(self, data: str, interval: float = None):
        """
        Writes text with the keyboard
        :param data:
        :param interval:
        :return:
        """
        if interval is None:
            pyautogui.write(data)
        else:
            pyautogui.write(data, interval=interval)

    def press(self, key: str):
        """
        Press a key
        """
        pyautogui.keyDown(key)

    def release(self, key: str):
        """
        Releases a key
        """
        pyautogui.keyUp(key)

