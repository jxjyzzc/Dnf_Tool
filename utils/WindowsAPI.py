#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/23 20:14
# @Author  : 肥鹅
# @file: WindowsAPI.py

import numpy,cv2
from PIL import Image
import win32gui,win32api,win32con,win32ui
import time,random

class WindowsAPI():

    def __init__(self):
        self.down_state = False
        self.currentKey = None
        pass

    def setKeyboard(self,keyboard):
        self.keyboard = keyboard
        return self.keyboard

    def getHwnd(self):

        hd = win32gui.GetDesktopWindow()
        print("桌面句柄", hd)

        hwndChildList = []
        win32gui.EnumChildWindows(hd, lambda hwnd, param: param.append(hwnd), hwndChildList)


        for hwnd in hwndChildList:
            # print(hwnd,win32gui.GetWindowText(hwnd))
            # if win32gui.GetWindowText(hwnd) == "Dungeon Fighter Online":
            if win32gui.GetWindowText(hwnd) == "地下城与勇士：创新世纪":
                print("游戏窗口句柄：", hwnd)
                self.hWnd = hwnd

                return hwnd

    def getGameImg(self):

        left, top, right, bot = win32gui.GetWindowRect(self.hWnd)
        width = right - left
        height = bot - top
        # 获取上下文句柄
        hWndDC = win32gui.GetWindowDC(self.hWnd)
        # 创建设备描述表
        mfcDC = win32ui.CreateDCFromHandle(hWndDC)
        # 内存设备描述表
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建位图对象
        saveBitMap = win32ui.CreateBitmap()
        # 分配存储空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        # 将位图对象选入到内存设备描述表
        saveDC.SelectObject(saveBitMap)
        #
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        #获取位图信息
        signedIntsArray = saveBitMap.GetBitmapBits(True)
        im_opencv = numpy.frombuffer(signedIntsArray, dtype = 'uint8')
        im_opencv.shape = (height, width, 4)

        # 内存释放
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(self.hWnd, hWndDC)

        return im_opencv

    def Foreground(self):
        """
        检查窗口是否激活（活动）
        :param hwnd: 窗口句柄
        :return: 布尔值，表示窗口是否激活
        """
        # 获取窗口的焦点状态
        focused_hwnd = win32gui.GetForegroundWindow()

        # 如果窗口句柄与焦点窗口句柄匹配，则表示窗口激活
        return self.hWnd == focused_hwnd


    def downDouble(self,key):
        if winApi.Foreground()== False:
            return
        print('inputKey:',key,"self.currentKey:",self.currentKey)    
        if (self.down_state == "double" and self.currentKey == key):
            return self.currentKey
        
        self.keyboard.release()  # 松开
        
        self.keyboard.send_data(key)  # 按下
        self.keyboard.release()       # 松开
        self.keyboard.send_data(key)  # 按下
        time.sleep(0.2)
        self.currentKey = key
        self.down_state = "double"
        return self.currentKey


    def release(self):
        print('winApi释放按键状态....')
        
        self.down_state = 'release'
        self.currentKey = None
        return self.keyboard.release() 

winApi = WindowsAPI()