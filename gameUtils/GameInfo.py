#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/17 22:58
# @Author  : 肥鹅
# @file: GameInfo.py

class GameInfo(object):

        def __init__(self):
                # 版本号
                self.Version = 1.2
                # 本地yolo地址
                self.yoloUrl = "http://127.0.0.1:5000/upload_image"
                # ch9329串口号
                self.comPort = ""
                # True为开启了辅助线程
                self.gameState = False
                # 辅助循环状态
                self.gameLoop = False
                # 所有技能
                self.totalSkills = {}
                # 地图房间技能
                self.roomSkills = {}
                # 游戏窗口标题
                self.gameTitle = "地下城与勇士：创新世纪"
                # 游戏窗口rect
                self.gameRect = {"x":0,"y":0,"width":0,"height":0}
                # 游戏窗口句柄
                self.gameHwnd = 0
                # 当前地图
                self.currentMap = None
                # 当前选择职业
                self.job = "自定义"
                # 所有配置的职业
                self.jobs = []
                # 人物高度
                self.playerHeight = 143
                # 人物速度
                self.speedX = 140
                self.speedY = 140
                # 房间出口
                self.roomExport = {}
                # 当前房间号
                self.roomId = None
                # 当前房间怪物数量
                self.roomMonsters = 0
                # 初始房间位置
                self.playerMap =(2,0)
                # boss房间位置
                self.bossMap = (2,6)
                # 游戏难度
                self.difficulty = ""
                #是否全图
                self.full_map = False
                #屏幕大小
                self.screen = {"w":0,"h":0}
                # 自动切换人物列表
                self.joblist = []
                # 开启自动切换人物
                self.autoSwitchEnabled = False

GAMEINFO = GameInfo()
print("基本信息初始化完成。")