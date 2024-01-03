#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/17 22:35
# @Author  : 肥鹅
# @file: LoadData.py

import xml.etree.ElementTree as ET

def loadRoomExport(path):

    

    roomExport = {
        "maps":{}
    }

    #读取xml文件
    tree = ET.parse(path)
    root = tree.getroot()

    for child in root:
        for sub_child in child:
            # print(sub_child)
            # 如果有属性
            if sub_child.attrib:
                sub_child_list = sub_child.attrib
                roomid = sub_child_list['roomid']
                export_x = sub_child_list['export_x']
                export_y = sub_child_list['export_y']
                direction = sub_child_list['direction']

                roomExport[child.tag][roomid] = {
                    "export_x":export_x,
                    "export_y":export_y,
                    "direction":direction,
                }

    return roomExport

# roomExport = loadRoomExport()
# print(roomExport)