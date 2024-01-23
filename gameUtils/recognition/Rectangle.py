# -*- coding: UTF-8 -*-

import cv2
import numpy as np
import math



"""
    标注装备方框，一般史诗能标注上即可
    :param im_opencv: 图片opencv数组
    :param max_y: 最大y坐标
    return: 按左上顶点为起点，顺时针，获取外接矩形的四个顶点的坐标
"""
def labelEquipment(im_opencv,max_y):
    crop_img = im_opencv[0:int(max_y),:]
    # cv2.imshow('crop_img',crop_img)
    # cv2.waitKey(0)

    rects=[]

    black_thr = 100

    #转换为灰度图
    gray = cv2.cvtColor(crop_img, cv2.COLOR_RGB2GRAY)

    #转为二值图
    ret, binary = cv2.threshold(gray, black_thr, 255, cv2.THRESH_BINARY)
    # cv2.imshow('binary',binary)

    # 膨胀算法的色块大小
    h, w = binary.shape
    hors_k = int(math.sqrt(w)*1.2)
    vert_k = int(math.sqrt(h)*1.2)

    # 白底黑字，膨胀白色横向色块，抹去文字和竖线，保留横线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (hors_k,1))
    hors = ~cv2.dilate(binary, kernel, iterations = 1) # 迭代两次，尽量抹去文本横线，变反为黑底白线

    # 白底黑字，膨胀白色竖向色块，抹去文字和横线，保留竖线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,vert_k))
    verts = ~cv2.dilate(binary, kernel, iterations = 1) # 迭代两次，尽量抹去文本竖线，变反为黑底白线

    # 横线竖线检测结果合并
    borders = cv2.bitwise_or(hors,verts)

    # cv2.imshow('borders',borders)
    # cv2.waitKey(0)
    img2 = None
    contours, hierarchy = cv2.findContours(borders,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt)>550 and cv2.contourArea(cnt)<1000:
            max_rect = cv2.minAreaRect(cnt)    # cnt这里是我们上个步骤中的到的面积最大的轮廓
    
            # 返回的 max_rect  就是下图中的rect，里面包括外接矩形的中心点，宽和高，以及偏移角度
            max_box = cv2.boxPoints(max_rect)
            max_box = np.int0(max_box)
            img2 = cv2.drawContours(im_opencv,[max_box],0,(0,255,0),2)
            
            # 外接矩形的四个顶点坐标
            pts1 = np.int0(max_box)
            # 根据4个点坐标变为(x,y,width,height) 的形式返回
            rect = cv2.boundingRect(pts1)
            # print('rect:',rect)
            # 按左上顶点为起点，顺时针，获取外接矩形的四个顶点的坐标
            rects.append(rect)

    # if img2 is not None:
    #     cv2.imshow('img2',img2)
    #     cv2.waitKey(0)

    return rects
"""
    四个点坐标，我们可以确定一个矩形区域。这四个点分别代表矩形的左上角、右上角、右下角和左下角
"""
def points_to_rect(points):
    # 确定矩形的左上角和右下角坐标
    left_top = min(points, key=lambda p: (p[0], p[1]))
    right_bottom = max(points, key=lambda p: (p[0], p[1]))

    # 计算矩形的宽度和高度
    width = right_bottom[0] - left_top[0]
    height = right_bottom[1] - left_top[1]

    # 输出矩形区域信息
    # print(f"矩形区域：({left_top}, {right_bottom})")
    # print(f"矩形尺寸：宽={width}，高={height}")
    return left_top, right_bottom, width, height

from typing import Tuple
import math

class Rectangle:
    def __init__(self, left: int, top: int, right: int, bottom: int):
        self.left = int(left)
        self.top = int(top)
        self.right = int(right)
        self.bottom = int(bottom)
        
        # 计算并存储中心点坐标
        self.center = (int((self.left + self.right) / 2), int((self.top + self.bottom) / 2))

    def center_distance(self, other_center: Tuple[int, int]) -> float:
        """计算当前矩形中心点与给定中心点之间的欧氏距离"""
        return math.sqrt((self.center[0] - other_center[0])**2 + (self.center[1] - other_center[1])**2)

    def is_center_near(self, other: 'Rectangle', distance_threshold: float) -> bool:
        """
        判断当前矩形的中心点是否在另一个矩形的中心点附近
        @param other: 另一个矩形
        @param distance_threshold: 距离阈值，单位同矩形坐标单位
        @return: 是否在指定距离阈值内
        """
        other_center = other.center
        return self.center_distance(other_center) <= distance_threshold

    '''
    原方法保留，但不再用于根据中心点附近的判断
    def is_contained_in(self, other: 'Rectangle') -> bool:
        return (self.left >= other.left and
                self.top >= other.top and
                self.right <= other.right and
                self.bottom <= other.bottom)
    '''



                                 
# 导出类
# __all__ = ['Rectangle']
    

if __name__ == '__main__':
    # 示例用法：
    rect1 = Rectangle(0, 0, 10, 10)
    rect2 = Rectangle(5, 5, 15, 15)
    distance_threshold = 3

    if rect1.is_center_near(rect2, distance_threshold):
        print("矩形1的中心点在矩形2的中心点附近")
    else:
        print("矩形1的中心点不在矩形2的中心点附近")