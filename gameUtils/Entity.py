#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/5 0:19
# @Author  : 肥鹅
# @file: Entity.py

class Entity(object):

    def __init__(self):
        self.name = ""
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

    def setPosition(self,_x,_y,_w,_h,_name):
        self.x = _x
        self.y = _y
        self.width = _w
        self.height = _h
        self.name = _name
