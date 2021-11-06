import win32gui
import win32ui
import win32con
import win32api
from ctypes import *
import win32clipboard


def window_capture(filename, x, y, w, h):
    hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    MoniterDev = win32api.EnumDisplayMonitors(None, None)
    '''
    w = MoniterDev[0][2][2]
    h = MoniterDev[0][2][3]
    '''
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    saveDC.BitBlt((x, y), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)

def copyboard(filename):
    aString=windll.user32.LoadImageW(0,filename,win32con.IMAGE_BITMAP,0,0,win32con.LR_LOADFROMFILE)
    print("copy")
    if aString !=0:
        print("cp2")
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_BITMAP, aString)
        win32clipboard.CloseClipboard()

def copystr(str):
    if str != None:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, str)
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, str)
        win32clipboard.CloseClipboard()

