# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 12:14:29 2020

@author: analoganddigital   ( GitHub )
"""
import numpy as np
import win32api
import win32con
import win32gui
import win32ui


def grab_screen(gameTitle=None,region=None):

    # _hwin_ = win32gui.GetDesktopWindow()
    hwin = win32gui.FindWindow(None, gameTitle) 
    
    if not hwin:
         print('找不到窗口---- %s!' %gameTitle)
         return None
    
    print('检测到游戏窗口---->%s' %gameTitle)


    if region:
            left,top,x2,y2 = region
            width = x2 - left + 1
            height = y2 - top + 1
    else:
        # width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        # height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        # left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
        # top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
        (left, top, right, bottom) = win32gui.GetWindowRect(hwin)
        region = (left, top, right, bottom)
        width = right - left + 1
        height = bottom - top + 1

    print('检测到游戏窗口区域---->(%s,%s,%s,%s)'%region)

    hwindc = win32gui.GetWindowDC(hwin)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)
    memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)
    
    signedIntsArray = bmp.GetBitmapBits(True)
    img = np.fromstring(signedIntsArray, dtype='uint8')
    img.shape = (height,width,4)

    srcdc.DeleteDC()
    memdc.DeleteDC()
    win32gui.ReleaseDC(hwin, hwindc)
    win32gui.DeleteObject(bmp.GetHandle())

    return img
