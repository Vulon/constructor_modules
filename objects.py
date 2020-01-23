from win32gui import SetForegroundWindow, ShowWindow, GetWindowRect, GetWindowText
from win32con import SW_MAXIMIZE

class Window:
    def __init__(self, hwnd, title):
        self.hwnd = hwnd
        if title is None:
            title = GetWindowText(hwnd)
        self.title = title
    def set_foreground(self):
        SetForegroundWindow(self.hwnd)
    def maximize_window(self):
        ShowWindow(self.hwnd, SW_MAXIMIZE)
    def get_window_rect(self):
        return GetWindowRect(self.hwnd)


class Picture:
    def __init__(self, image=None, file_path=None):
        if image:
            self.image = image
        elif file_path:
            from PIL import Image
            self.image = Image.open(file_path)
        else:
            raise Exception("Input must contain PIL image, or file_path to image")

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.coords = (x, y)