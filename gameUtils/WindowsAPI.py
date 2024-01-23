#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/23 20:14
# @Author  : 肥鹅
# @file: WindowsAPI.py

import numpy,cv2
from gameUtils.app import find_app
from PIL import Image
from config.cfg import *
import win32gui,win32api,win32con,win32ui
import pyautogui
import time,random
import logging
from loguru import logger
# from gameUtils.GameInfo import GAMEINFO


common_path = 'imgs/{}_{}/{}'.format(800, 600, '{}')

select_role_path = common_path.format('select_role.png')
start_game_path = common_path.format('start_game.png')

class WindowsAPI():

    def __init__(self):
        self.serial = serial
        self.keyboard = keyboard
        self.mouse = mouse
        self.down_state = False
        self.currentKey = None
        pass

    # '''释放windowsAPI时触发'''    
    # def __del__(self):
    #     if self.serial and self.serial != -1:
    #         logger.info('关闭模拟键鼠模块')
    #         if self.keyboard:
    #             # 放开按键
    #             keyboard.release()

    #         serial.ser.close()
    #         self.serial = None
    #         self.keyboard = None
    #         pass

    def getKeyboard(self):
        return self.keyboard
    
    def getMouse(self):
        return self.mouse

    def setHwnd(self,hwnd):
        logger.debug("绑定窗口句柄{}", hwnd)
        self.hWnd = hwnd


    def getHwnd(self, title='地下城与勇士：创新世纪'):

        hd = win32gui.GetDesktopWindow()
        logger.debug("桌面句柄{}", hd)

        hwndChildList = []
        win32gui.EnumChildWindows(hd, lambda hwnd, param: param.append(hwnd), hwndChildList)


        for hwnd in hwndChildList:
            # print(hwnd,win32gui.GetWindowText(hwnd))
            # if win32gui.GetWindowText(hwnd) == "Dungeon Fighter Online":
            if win32gui.GetWindowText(hwnd) == title:
                logger.info("窗口句柄：{}", hwnd)
                self.setHwnd(hwnd)
                self.showWindow()
                return hwnd



   

    ''' 激活窗口 '''
    def showWindow(self):
        if not self.hWnd:
            logger.warning("未找到游戏窗口句柄")
            return False
              
        win32gui.ShowWindow(self.hWnd,win32con.SW_SHOW)
        # 设置窗口为前台
        win32gui.SetForegroundWindow(self.hWnd)
        return True
        

    """
        查找图片
        :param img: 被查找的图片
        :param template: 用来查找图片
        :return: 返回坐标
    """
    def find_img(self,img,template,threshold=0.8):
        try:
            res = cv2.matchTemplate(img,template,cv2.TM_CCOEFF_NORMED)
            min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)

            if max_val < threshold:
                return None
            return max_loc
        except Exception as e:
            if img is not None and img.shape[0]>0 and img.shape[1]>0:
                cv2.imwrite('error_full_img',img)
            if template is not None and template.shape[0]>0 and template.shape[1]>0:    
                cv2.imwrite('error_template_img',template)
            logger.error("查找图片失败：{},出错文件:{},行号:",e,
                         e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno)
            return None
        
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


    """
        随机延迟
        :param delay1: 延迟1
        :param delay2: 延迟2
        :return: 返回延迟

    """
    def randomDelay(self,delay1,delay2):
        time.sleep(random.uniform(delay1,delay2))


    """
        按下按键
        :param key: 按键
        :return: 返回按键

    """
    def keyDown(self,key):
        # if winApi.Foreground()== False:
        #     return
        self.keyboard.send_data(key)  # 按下
        self.keyboard.release()       # 松开
        self.currentKey = key
        self.down_state = "down"
        return self.currentKey
    
    """
        快速按两次按键
        :param key: 按键
        :return: 返回按键
    """
    def keyDownDouble(self,key):
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


    def keyRelease(self):
        print('winApi释放按键状态....')
        
        self.down_state = 'release'
        self.currentKey = None
        return self.keyboard.release() 
    
    '''
        鼠标绝对移动
        x: 横坐标
        y: 纵坐标
        offex_x: 横坐标偏移量
        offex_y: 纵坐标偏移量
    '''
    def moveRel(self, x, y, offex_x, offex_y):
        my_ratio = 9

        dis_offex_x = abs(offex_x)
        dis_offex_y = abs(offex_y)
        loop_x = offex_x / my_ratio
        loop_y = offex_y / my_ratio
        mod_x = offex_x % my_ratio
        mod_y = offex_y % my_ratio
        min_loop = int(min(abs(loop_x),abs(loop_y)))
        max_loop = int(max(abs(loop_x),abs(loop_y)))
        # print(f'min_loop:{min_loop},max_loop:{max_loop},mod_x:{mod_x},,mod_y:{mod_y}')
        dir = [0,0]
        for i in range(min_loop): 
            if loop_x > 0:
                dir[0] = my_ratio
                dis_offex_x -= my_ratio
            elif loop_x < 0:
                dir[0] = -my_ratio
                dis_offex_x -= my_ratio
            if loop_y > 0:
                dir[1] = my_ratio
                dis_offex_y -= my_ratio
            elif loop_y < 0:
                dir[1] = -my_ratio
                dis_offex_y -= my_ratio
            # print('i:',i,',dir相对移动：',dir[0],',',dir[1]) 
            # print('i:',i,',curr_offex_x:',dis_offex_x,',curr_offex_y:',dis_offex_y)
            mouse.send_data_relatively(dir[0],dir[1])
            time.sleep(0.006)

        dir = [0,0]
        # 与目标点x轴距离小于阈值，只移动y轴坐标
        if dis_offex_x < my_ratio:
            for i in range(max_loop-min_loop):
                if loop_y > 0 and abs(dis_offex_y) >= my_ratio:
                    dir[1] = my_ratio
                    dis_offex_y -= my_ratio
                elif loop_y < 0 and abs(dis_offex_y) >= my_ratio:
                    dir[1] = -my_ratio
                    dis_offex_y -= my_ratio
                # print('i:',i,',y相对移动：',0,',',dir[1]) 
                mouse.send_data_relatively(0,dir[1])
                time.sleep(0.006)
        # 与目标点y轴距离小于阈值，只移动x轴坐标
        if dis_offex_y < my_ratio:
            for i in range(max_loop-min_loop):
                if loop_x > 0 and abs(dis_offex_x) >= my_ratio:
                    dir[0] = my_ratio
                    dis_offex_x -= my_ratio
                elif loop_x < 0 and abs(dis_offex_x) >= my_ratio:
                    dir[0] = -my_ratio
                    dis_offex_x -= my_ratio
                print('i:',i,',x相对移动：',dir[0],',',0) 
                mouse.send_data_relatively(dir[0],0)
                time.sleep(0.006)

        x_, y_ = pyautogui.position()
        return x_, y_

    '''
        鼠标绝对定位移动并点击
        :param x: 横坐标
        :param y: 纵坐标
        :return: 返回坐标
    '''    
    def moveAbsClick(self, x, y):
        self.mouse.send_data_absolute(x, y)
        time.sleep(random.uniform(0.1,0.3))
        self.mouse.click()
        return x, y

winApi = WindowsAPI()