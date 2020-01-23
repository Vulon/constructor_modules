from PIL import Image
import numpy as np
from PIL import ImageGrab
import win32gui
import win32api
import win32con

from objects import Window

def get_window_by_name(name):
    winlist = []

    def enum_cb(hwnd, results):
        if len(win32gui.GetWindowText(hwnd)) > 0:
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

    win32gui.EnumWindows(enum_cb, [])
    print(winlist)

    list = [(hwnd, title) for hwnd, title in winlist if name.lower() in title.lower()]
    return Window(list[0][0], list[0][1])

