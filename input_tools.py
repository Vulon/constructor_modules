from win32api import SetCursorPos
import win32clipboard


def move_mouse(position_coordinates):
    SetCursorPos(position_coordinates.coords)

def read_clipboard():
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return data

def paste_to_clipboard(text):
    win32clipboard.OpenClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, str(text))
    win32clipboard.CloseClipboard()