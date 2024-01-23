import sys,os
import math
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)
import cv2
import numpy as np
from gameUtils.WindowsAPI import winApi
from tool.ocrutil import cv_imread,find_one_picd




  
def calculate_gray_value(img):
   # 分割RGB通道
   r, g, b = cv2.split(img)
 
   # 转换成数组
   r1 = np.asarray(r, np.int16)
   g1 = np.asarray(g, np.int16)
   b1 = np.asarray(b, np.int16)
   # 令一种转换方式
   # r = r.astype(np.int16)
   # g = g.astype(np.int16)
   # b = b.astype(np.int16)
 
   # 计算各通道之间的方差
   diff1 = (r1 - g1).var()
   diff2 = (g1 - b1).var()
   diff3 = (b1 - r1).var()
   diff_sum = (diff1 + diff2 + diff3) / 3.0
   return diff_sum
   


finish_img = cv_imread('map/img/map_finish.jpg')

pic = cv_imread('test/img/无疲劳.jpg')
# pic = cv2.imread("194.jpg", cv2.IMREAD_UNCHANGED) # 自己想要分析的照片
findFlag,coordinate =  find_one_picd(pic,'map/img/map_finish.jpg',0.8)
if findFlag:
    print(coordinate)
    print(calculate_gray_value(pic[coordinate[3]:coordinate[-1],coordinate[2]:coordinate[-2]]))
    cv2.rectangle(pic, (coordinate[2], coordinate[3]), (coordinate[4], coordinate[5]), (0, 0, 255), 2)

# loc =  winApi.find_img(pic,finish_img,0.9)
# if loc is not None:
#     print('loc:',loc)
#     print('shape:',finish_img.shape)
#     print(calculate_gray_value(pic[loc[1]:loc[1]+finish_img.shape[0],loc[0]:loc[0]+finish_img.shape[1]]))  
#     cv2.rectangle(pic, (loc[0], loc[1]), (loc[0]+finish_img.shape[1], loc[1]+finish_img.shape[0]), (0, 0, 255), 2)

cv2.imshow('pic',pic)


pic2 = cv_imread('test/img/有疲劳.jpg')
findFlag,coordinate =  find_one_picd(pic2,'map/img/map_finish.jpg',0.8)
if findFlag:
    print(coordinate)
    print(calculate_gray_value(pic2[coordinate[3]:coordinate[-1],coordinate[2]:coordinate[-2]]))
    cv2.rectangle(pic2, (coordinate[2], coordinate[3]), (coordinate[4], coordinate[5]), (0, 0, 255), 2)

# pic2 = cv_imread('test/img/有疲劳.jpg')
# loc =  winApi.find_img(pic2,finish_img,0.9)
# if loc is not None:
#     print('loc:',loc)
#     print('shape:',finish_img.shape)
#     print(calculate_gray_value(pic2[loc[1]:loc[1]+finish_img.shape[0],loc[0]:loc[0]+finish_img.shape[1]]))  
#     cv2.rectangle(pic2, (loc[0], loc[1]), (loc[0]+finish_img.shape[1], loc[1]+finish_img.shape[0]), (0, 0, 255), 2)
cv2.imshow('pic2',pic2)

cv2.waitKey(0)    