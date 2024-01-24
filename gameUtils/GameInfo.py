import os,sys
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
## parenddir 是当前代码文件所在目录的父目录
parenddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
# sys.path.append(parenddir)
from configobj import ConfigObj

# *** 配置文件预处理 *** #
path = os.path.dirname(os.path.dirname(__file__)) + "/config/game_info.ini"
config = ConfigObj(path,encoding='UTF8')

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
                self.playerMap =(4,1)
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

                self.powerlist = []
                # 开启自动切换人物
                self.autoSwitchEnabled = False

         # 读取配置文件信息
        def queryJobList(self):
                if 'jobList' in config['finishedRole']:
                        self.joblist = config['finishedRole']['jobList'] 
                        self.powerlist = config["finishedRole"]['powerList']
                        # print('game_info.ini load配置jobList：',config['finishedRole']['jobList'])
                return self.joblist ,self.powerlist        

        def modifyRolePosition(self,jobList,powerList):
                config['finishedRole']['jobList'] = jobList
                config['finishedRole']['powerList'] = powerList
                self.joblist = jobList
                self.powerlist = powerList
                config.write()                   
                print('game_info.ini更新 jobList',config['finishedRole']['jobList'])
                print('game_info.ini更新 powerList',config['finishedRole']['powerList'])

        def saveCurRoleIndex(self,curRoleIndex):
              config['finishedRole']['curRoleIndex'] = curRoleIndex   
              config.write()

        def getCurRoleIndex(self):
              return config['finishedRole']['curRoleIndex']             

GAMEINFO = GameInfo()

  

print("基本信息初始化完成。")