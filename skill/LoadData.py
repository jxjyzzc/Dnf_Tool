#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/26 2:23
# @Author  : 肥鹅
# @file: LoadData.py

import xml.etree.ElementTree as ET

import sys
sys.path.append('.')

from gameUtils.GameInfo import GAMEINFO 

def loadTotalSkill(jobName,path):

    tree = ET.parse(path)
    root = tree.getroot()

    totalskill = []
    for child in root:
        if child.attrib:
            childattr = child.attrib
            _job = childattr['jobName']
            # 过滤掉不是本职业的职业描述
            if  jobName != _job:
                continue
        for sub_child in child:
            if sub_child.attrib:
                sub_child_list = sub_child.attrib
                id = sub_child_list['id']
                cd = sub_child_list['cd']
                costTime = sub_child_list['costTime']
                name = sub_child_list['name']
                # print(id,cd,name,costTime)
                totalskill.append([id,cd,name,costTime])

    return totalskill


def loadRoomSkill(path):

    tree = ET.parse(path)
    root = tree.getroot()

    room_skills = []
    for child in root:
        # skills_list = []
        for sub_child in child:
            row_list = []
            for cell in sub_child:
                chars_list = []
                for chars in cell:
                    char_list = []
                    for char in chars:
                        # print(char.text)
                        char_list.append(char.text)

                    chars_list.append(char_list)
                row_list.append(chars_list)

            room_skills.append(row_list)
            # print(row_list)
    return room_skills



def loadJob(jobName,roomName):

    tree = ET.parse("skill/joblist.xml")
    root = tree.getroot()

    for child in root:

        if child.attrib:
            sub_child_list = child.attrib

            sub_name = sub_child_list['name']
            # print('sub_name:',sub_name)
            if jobName == sub_name:
                sub_height = sub_child_list['height']
                GAMEINFO.playerHeight = int(sub_height)

                skill_path = child.find('skills').text
                roomskill_path = child.find("roomskill[@room_name='"+roomName+"']").text
                

                total_skill = loadTotalSkill(jobName,skill_path)
                room_skill = loadRoomSkill(roomskill_path)
                # print(skill_path,roomskill_path)
                return total_skill,room_skill
            
    print('未匹配',jobName+'技能，请检查配置')
    return None,None

if __name__ == "__main__":
    t_skill,room_skill = loadJob('阿修罗','bydt')
    # skill = loadRoomSkill('skill/current_nvqigoong_skill.xml')
    # print('所有技能',t_skill)
    skill = ['S','CR']
    print('房间技能：',skill)

    import time
    ## s释放技能，如果当前地图技能释放完毕则进行平a
    def mapSkill(_t_skill,_skill):
        if _skill != None:

            for v in _skill: 
                for k in _t_skill:
                    if k[0] == v:
                        # k[3]：total_skill.xml添加技能冷却时间（包括释放动画）字段
                        tmpFlag = k[3]
                        costTime = k[3]
                        if costTime != 0:
                            t = int(time.time())
                            if t > int(float(k[1]) + float(k[3])):
                                tmpFlag = 0
        
                        if tmpFlag == 0:
                            tmpFlag = int(time.time())
                            return (v,float(costTime))
                    
        return ("X",0)
    
    k,costTime = mapSkill(t_skill,skill)
    print('当前图应按键：',k,'按住时间：',costTime)