#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/17 22:58
# @Author  : 肥鹅
# @file: GameInfo.py

class GameInfo(object):

    def __init__(self):
        self.playerSpeed = {"x":0,"y":0}
        self.rooId = 0
        self.playerHeight = 0

GAMEINFO = GameInfo()