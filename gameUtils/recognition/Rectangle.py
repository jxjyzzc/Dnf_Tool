# -*- coding: UTF-8 -*-

import cv2
import numpy as np

class RecRectangle():

    def __init__(self,bg):
        self.background = bg
        pass


    def cross_point(self,line1, line2):  # 计算交点函数
        #是否存在交点
        point_is_exist=False
        x=0
        y=0
        x1 = line1[0]  # 取四点坐标
        y1 = line1[1]
        x2 = line1[2]
        y2 = line1[3]

        x3 = line2[0]
        y3 = line2[1]
        x4 = line2[2]
        y4 = line2[3]

        if (x2 - x1) == 0:
            k1 = None
        else:
            k1 = (y2 - y1) * 1.0 / (x2 - x1)  # 计算k1,由于点均为整数，需要进行浮点数转化
            b1 = y1 * 1.0 - x1 * k1 * 1.0  # 整型转浮点型是关键

        if (x4 - x3) == 0:  # L2直线斜率不存在操作
            k2 = None
            b2 = 0
        else:
            k2 = (y4 - y3) * 1.0 / (x4 - x3)  # 斜率存在操作
            b2 = y3 * 1.0 - x3 * k2 * 1.0

        if k1 is None:
            if not k2 is None:
                x = x1
                y = k2 * x1 + b2
                point_is_exist=True
        elif k2 is None:
            x=x3
            y=k1*x3+b1
        elif not k2==k1:
            x = (b2 - b1) * 1.0 / (k1 - k2)
            y = k1 * x * 1.0 + b1 * 1.0
            point_is_exist=True
        return point_is_exist,[x, y]

    # 去除图片背景
    def remove_background(self,img):
       
        # 转换到HSV
        # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # cv2.imshow('hsv', hsv)
        # cv2.waitKey(0)

        # 设定蓝色的阈值
        # lower_blue = np.array([100, 43, 50])
        # upper_blue = np.array([124, 255, 255])
    
        # 根据阈值构建掩膜
        # mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
        # 对元图像和掩膜进行位运算
        # res = cv2.bitwise_and(img, img, mask=mask)
    
        # 显示图像
        # cv2.imshow('mask', mask)
        # cv2.imshow('res', res)
        # cv2.waitKey(0)
       
    #    mask = np.zeros(img.shape[:2], np.uint8)

    #    bgdModel = np.zeros((1, 65), np.float64)
    #    fgdModel = np.zeros((1, 65), np.float64)
    #    rect = (0, 0, img.shape[1], img.shape[0])
    #    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        
    #    mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
    #    diff = img * mask2[:,:, np.newaxis]
    # 前景图像与背景图像相减
        diff = cv2.absdiff(self.background, img)
        # cv2.imshow('diff', diff)
        # cv2.waitKey(0)
        return diff
       


    # 识别当前选择人物的矩形
    def rectangle_recognition(self,img):
        front_img = self.remove_background(img)
        
        # 转灰度图
        gray=cv2.cvtColor(front_img,cv2.COLOR_BGR2GRAY)
        # 利用cv2.minMaxLoc寻找到图像中最亮和最暗的点
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
        # 在图像中绘制结果
        # cv2.circle(front_img, maxLoc, 5, (255, 0, 0), 2)
        # cv2.imshow('front_img', front_img)
        # cv2.waitKey(0)

        #高斯模糊
        gray=cv2.GaussianBlur(gray,(3,3),0)
        gray = cv2.medianBlur(gray,3)
        
        # cv2.imshow('gray', gray)
        # cv2.waitKey(0)
       # 使用Canny边缘检测算法找出边缘，并将结果存储在edges变量中。
        edges = cv2.Canny(gray, 165, 275)
        # cv2.imshow('Edges1', edges)
        # cv2.waitKey(0)
        
         # 边缘膨胀
        # kernel = np.ones((4, 4), np.uint8)
        # cv2.dilate(edges, kernel, 3)
        # cv2.imshow('Edges2', edges)
        # cv2.waitKey(0)


        #霍夫变换
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 110, minLineLength=110, maxLineGap=10)
        print('lines:',lines)

        
        lines1 =lines[:, 0, :] # 提取为二维
        for x1, y1, x2, y2 in lines1[:]:
            cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # cv2.imshow('line1', img)
        # cv2.waitKey(0)


        cross_points = []
        for x1, y1, x2, y2 in lines1[:]:
            for x3,y3,x4,y4 in lines1[:]:
                point_is_exist, [x, y]= self.cross_point([x1, y1, x2, y2],[x3,y3,x4,y4])
                if point_is_exist:
                    # cv2.circle(img,(int(x),int(y)),5,(0,0,255),3)
                    cross_points.append([x, y])

        rectangle_points = []
        # 如果交点数大于4个，并且有2组交点的x坐标差在127左右，y坐标差在206左右，则认为是矩形
        if len(cross_points) >= 4:
            
            cross_points_np = np.array(cross_points)
            # print('cross_points=',cross_points)
            # print('cross_points_np=',cross_points_np)
            # print('np.roll(cross_points_np[:, 0], 1)',np.roll(cross_points_np[:, 0], 1))

            # 筛选x坐标差在123到128之间且y坐标差值为0的点
            # 筛选y坐标差在205到210之间且x坐标差值为0的点
            # 筛选条件
            x_diff_condition = (np.abs(cross_points_np[:, 0] - np.roll(cross_points_np[:, 0], 1)) >= 123) & \
                (np.abs(cross_points_np[:, 0] - np.roll(cross_points_np[:, 0], 1)) <= 128) 
            y_diff_condition = (np.abs(cross_points_np[:, 1] - np.roll(cross_points_np[:, 1], 1)) >= 205) & \
                (np.abs(cross_points_np[:, 1] - np.roll(cross_points_np[:, 1], 1)) <= 210) 

            # print('x_diff_condition:',x_diff_condition)
            # print('y_diff_condition:',y_diff_condition)
            # 应用筛选条件
            filtered_points = cross_points_np[ x_diff_condition | y_diff_condition ]

            # 转为二维数组
            rectangle_points = filtered_points.reshape(-1, 2)

            # print('rectangle_points:',rectangle_points)

        

        for (x,y) in rectangle_points:
            print('rectangle points:',(x,y))
            cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), 3)   

        return rectangle_points                             



if __name__ == '__main__':
    #图片路径
    bg = cv2.imread('startUI/img/rolebackgroud.jpg')
    bg = bg[85:546,0:782]
    rectangle = RecRectangle(bg)
    imgPath=r'test/img/roleSelect6.jpg'
    img=cv2.imread(imgPath)
    roi_img = img[85:546,0:782]
    rectangle.rectangle_recognition(roi_img)

    cv2.imshow('Result', img)
    cv2.waitKey (0)