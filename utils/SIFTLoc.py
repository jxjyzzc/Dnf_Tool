#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/7/4 0:34
# @Author  : 肥鹅
# @file: test.py

import cv2
import numpy as np

class SIFTLoc():

    def __init__(self):
        self.sift = cv2.SIFT_create()
        # 创建FLANN匹配器
        self.matcher = cv2.FlannBasedMatcher()

    def setMaxImg(self,path):
        self.maxMap_img = cv2.imread(path)

    def setMinImg(self, img):
        self.h_img = img #cv2.imread(img)

    def getSiftLoc(self,max_path,min_img):
        try:
            self.setMaxImg(max_path)
            self.setMinImg(min_img)
            # 在图像中检测特征点和计算描述符
            keypoints1, descriptors1 = self.sift.detectAndCompute(self.maxMap_img, None)
            keypoints2, descriptors2 = self.sift.detectAndCompute(self.h_img, None)
            
            # 使用 KNN 匹配得到最佳匹配结果
            k = 2  # 取前两个最佳匹配
            matches = self.matcher.knnMatch(np.asarray(descriptors1, np.float32) , np.asarray(descriptors2,np.float32), k)
            
            # 进行匹配结果筛选
            good_matches = []
            for m, n in matches:
                if m.distance < 0.85 * n.distance:
                    # print(type(m))
                    # print(keypoints1[m.queryIdx].pt)
                    good_matches.append(m)
            
            # 提取匹配点对的位置
            points1 = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            points2 = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # 计算图2在图1中的变换矩阵
            M, mask = cv2.findHomography(points2, points1, cv2.RANSAC, 5.0)
            
            # 对图2进行透视变换
            height, width, _ = self.maxMap_img.shape
            aligned_image2 = cv2.warpPerspective(self.h_img, M, (width, height))
            
            # 将图2融合在图1的最佳匹配位置上
            result = cv2.addWeighted(self.maxMap_img, 0.5, aligned_image2, 0.5, 0)
            # print("M:",M)
            
            #输出最佳匹配位置
            # print("Best match position: ({}, {})".format(M[0, 2], M[1, 2]))
            #返回X,Y坐标
            return M[0, 2], M[1, 2]
        except Exception as e:
            print("特征检测遇到错误",e)
            return None,None
        
        
siftLoc = SIFTLoc()