#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/23 20:21
# @Author  : 肥鹅
# @file: MiniMapTools.py

import cv2

class MiniMapTools():

    def __init__(self):

        pass

    def getMimiMapImg(self,im_opencv):
        #小地图
        im_opencv = im_opencv[27:27+75,800-6-128:800-6]
        self.im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
        return self.im_opencv

    def matchTemplate(self,template):
        #模板匹配
        res = cv2.matchTemplate(self.im_opencv,template,cv2.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)

        if max_val < 0.6:
            return None

        x,y = list(max_loc)
        hero_h,hero_w = template.shape[:2]

        #人物小地图坐标
        x = x + hero_w / 2
        y = y + hero_h / 2

        #小地图的宽高
        minimap_w = 128
        minimap_h = 75

        #小方格宽高
        width = minimap_w / 7
        height = minimap_h / 4

        row = x // width
      
        # print("当前人物所在地图房间号：",row)

        column = y // height

        room_id = str(int(column)) + "_" + str(int(row))
        # print("当前人物所在地图房间号：",room_id)
        return room_id 

    def getPlayerRoomId(self):
        template = cv2.imread("map_hero.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)
        return self.matchTemplate(template)
        

    def getBossRoomId(self):
        template = cv2.imread("map_boss.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)
        return self.matchTemplate(template)
    
    def getLiefengRoomId(self):
        template = cv2.imread("map_liefeng.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)
        return self.matchTemplate(template)    

miniMapTools = MiniMapTools()

