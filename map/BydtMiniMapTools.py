#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/6/23 20:21
# @Author  : 肥鹅
# @file: MiniMapTools.py

import cv2
import math
import numpy as np
import os
from loguru import logger

class BydtMiniMapTools():

    def __init__(self):
         #小地图的宽高
        self.minimap_w = 130
        self.minimap_h = 79
        pass

    # 测试用
    def getTestMapImg(self,im_opencv):
        self.im_opencv = im_opencv
        print('testMap shape:',self.im_opencv.shape)
        return self.im_opencv

    def getMimiMapImg(self,im_opencv):
        if im_opencv is None:
            return None
        #小地图
        im_opencv = im_opencv[25:25+self.minimap_h,800-6-self.minimap_w:800-6]
        # print('尝试保存截取图片',os.path.abspath('img/output1.png'))
        cv2.imwrite(os.path.abspath('test/img/output1.png'), im_opencv)
        self.im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
        # cv2.imwrite(os.path.abspath('test/img/output2.png'), self.im_opencv)
        # cv2.imshow('im_opencv',im_opencv)
        # self.im_opencv = im_opencv
        return self.im_opencv
    
    def matchTemplate(self,template):
        #模板匹配
        res = cv2.matchTemplate(self.im_opencv,template,cv2.TM_CCOEFF_NORMED)
        min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
        if max_val < 0.7:
            return None
        
        x,y = list(max_loc)
        hero_h,hero_w = template.shape[:2]

        #人物小地图坐标
        x = x + hero_w / 2
        y = y + hero_h / 2

        # print('人物小地图坐标：',x,y)

        #小方格宽高
        width = round(self.minimap_w / 7, 0)
        height = round(self.minimap_h / 4, 0)
        # print('小方格宽高 %d,%d' %(width,height))

        row = x // width
        
        # print("当前人物所在地图房间号row：",row)


        column = y // height
       
        # print("当前人物所在地图房间号col：",column)
        
        if column>=6:
            print('未找到房间！！')
            return None

        room_id = str(int(column)) + "_" + str(int(row))
        # print("当前人物所在地图房间号：",room_id)
        return room_id 

    def customPlayerRoomId(self):
        testImgs = ["1_2","3_4"]
        for tImg in testImgs:
            template = cv2.imread(r"map/img/bydt/bydt_p_"+tImg+".png")
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)
            try:
                res = cv2.matchTemplate(self.im_opencv,template,cv2.TM_CCOEFF_NORMED)
                min_val,max_val,min_loc,max_loc = cv2.minMaxLoc(res)
                if max_val > 0.7:
                    return tImg
            except Exception as e:
                continue

        return None

    def getPlayerRoomId(self):
        # 神界图部分地图没有英雄图标，直接拿指定模板来匹配
        preRoomId = self.customPlayerRoomId()
        print('getPlayerRoomId preRoomId:',preRoomId)
        if preRoomId is not None:
            return preRoomId

        template = cv2.imread(r"map/img/map_hero.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)
        # cv2.imshow('template',template)
        # cv2.waitKey(0)
    
       # 检查模板图像和输入图像的深度和类型是否正确
        assert self.im_opencv.dtype == template.dtype, "图像的深度不正确"
        assert self.im_opencv.ndim == template.ndim == 3, "图像的维度不正确"
        return self.matchTemplate(template)
        


    def getBossRoomId(self):

        template = cv2.imread(r"map/img/map_boss.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)

        return self.matchTemplate(template)
    
    def getLiefengRoomId(self):

        template = cv2.imread(r"map/img/map_liefeng.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)

        return self.matchTemplate(template)
    

    def getJingyingRoomId(self):

        template = cv2.imread(r"map/img/map_jingying1.png")
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)

        # cv2.imshow('test1',template)
        # cv2.waitKey(0)

        roomId = self.matchTemplate(template)

        if roomId is None:
            template = cv2.imread(r"map/img/map_jingying2.png")
            # cv2.imshow('test2',template)
            # cv2.waitKey(0)
            template = cv2.cvtColor(template, cv2.COLOR_BGRA2RGB)
            roomId = self.matchTemplate(template)

        return roomId

miniMapTools = BydtMiniMapTools()



if __name__ == "__main__":
    import os
    
    # 测试未匹配图片
    # img_path = os.path.abspath("test/img/error1.jpg")
    img_path = os.path.abspath(r"test/img/output1.png")
    cv_img = cv2.imread(img_path)
    cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGRA2RGB)
    cv2.imshow("test",cv_img)
    cv2.waitKey(0)
    
    miniMapTools.getTestMapImg(cv_img)
    print("在第%s个房间" % miniMapTools.getPlayerRoomId())

    print("BOSS第%s个房间" % miniMapTools.getBossRoomId())
    # jingying_roomid = miniMapTools.getJingyingRoomId()
    # print("精英房间:%s" % jingying_roomid)
    # if cv2.waitKey(0) & 0xFF == 27:
    #     cv2.destroyAllWindows()    