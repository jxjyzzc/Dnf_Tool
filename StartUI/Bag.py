import os,sys
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
## parenddir 是当前代码文件所在目录的父目录
parenddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parenddir)

from typing import List
from gameUtils.WindowsAPI import winApi
from tool.ocrutil import ocrUtil,find_one_picd
from gameUtils.recognition.Rectangle import Rectangle,labelEquipment
import gameUtils.app as app

from loguru import logger 
import random,time
import cv2
import numpy as np
import array


class Bag:

    """
        bag
        
        
    """
    def __init__(self,bag_max_row=4,dismant_highest_level=68):
        # 键盘操作接口
        # self.keyboard = winApi.getKeyboard()
        self.mouse = winApi.getMouse()
        handle, app_head, app_tail, app_width, app_height = app.find_app('地下城与勇士：创新世纪')
        # 装备栏左上角
        self.app_head = app_head
        self.hwnd = winApi.getHwnd()
        self.setInitStatus()
        self.bag_width = 30.5
        self.bag_height = 30.5
        self.bag_max_row = bag_max_row
        self.dismant_highest_level = dismant_highest_level

    """
        鼠标移动到固定位置,避免上一次鼠标位置干扰图像查找
    """
    def setInitMousePos(self):
        start_x,start_y = (self.app_head[0]+600+random.randint(-3,3),self.app_head[1]+230+random.randint(3,8))
        self.mouse.send_data_absolute(start_x,start_y)
        time.sleep(0.2)
        return start_x,start_y

    """
        box_head 装备栏左上角坐标
    """
    def setInitStatus(self):
        self.box_head = None
        self.setInitMousePos()
        
        full_img = winApi.getGameImg()
        time.sleep(0.2)
        # equip_tab
        has_equip, coordinate = find_one_picd(full_img,'startUI/img/dismant/equip_tab.jpg',0.7)
        if has_equip is False:
            logger.warning('背包未找到 equip_tab')
        else:
            init_x = int(coordinate[2]-7.5)
            init_y = int(coordinate[-1]+8)
            logger.debug('背包 init_x: {},init_y:{}',init_x,init_y)
            self.box_head = (init_x,init_y)
        return self.box_head

    """
        
        找到bag的矩阵区域
        :return: rectangle数组
    """
    def find_bag_equipmentROI(self):
        self.setInitMousePos()
        full_img = winApi.getGameImg()
        # 获取装备坐标信息 471,266 715,500
        across_bag_img = full_img[self.box_head[1]:500,self.box_head[0]:715]
        # cv2.imshow('across_bag_img',across_bag_img)
        # cv2.waitKey(2000)
        # recRectangle = Rectangle(across_bag_img,self.bag_max_row*first_bag_height)
        points = labelEquipment(across_bag_img,self.bag_max_row*self.bag_height)
        if len(points) == 0:
            logger.warning('未找到 equipemnts roi')
            return None
        rois=[]

        for i in range(len(points)):
            (x,y,w,h) = points[i]
            left,right,top,bottom = x, x + w, y,y + h
            rois.append(Rectangle(left, top, right, bottom))
        
        return rois

    def containInROIs(self,a1: Rectangle, rois: List[Rectangle]) -> Rectangle:
        for roi in rois:
            # 背包截取不准确，其实确保a1点在右下方一定位置简化情况
            distance_threshold = 5
            # logger.debug('a1 {} left, top, right, bottom:{}',(a1.left,a1.top,a1.right,a1.bottom),(roi.left, roi.top, roi.right, roi.bottom))
            if a1.is_center_near(roi,distance_threshold):
                return roi
        return None


 #   图片预处理
    def imgPreprocessing(self,pre_img):
        height, width, deep = pre_img.shape
        gray = cv2.cvtColor(pre_img, cv2.COLOR_BGR2GRAY) # cv2.COLOR_BGR2GRAY 将BGR格式转换成灰度图片
        dst = np.zeros((height, width, 1), np.uint8) #生成一张纯黑色图
        
        for i in range(0, height):  # 反相 转白底黑字
            for j in range(0, width):
                grayPixel = gray[i, j]
                dst[i, j] = 255 - grayPixel
        #走完这一步，已经实现了 转白底黑字，但是白色低背景不是最亮的
        #再用cv2.threshold进行二值化，使黑色部分更黑，白的更白
        ret, img = cv2.threshold(dst, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        image = np.array(img)
        return image

    """
        移动到背包装备栏指定位置，并返回当前背包装备等级
        bag_index 要访问的背包序号 1开始
        rois 要访问的背包区域，可选
    """
    def moveBagEquipmentGetLevel(self,bag_index,rois: List[Rectangle]=None):
        cur_index = int(bag_index)-1
        '''
            单重循环遍历大致思路：

            1、取第一格背包的中心点坐标。

            2、获取一格背包的宽度和高度是多少。

            3、 遍历公式：第二格背包中心x坐标=背包第一格中心X坐标 + (2 mod 背包总列数) * 每格宽

            第二格背包中心y坐标=背包第一格中心Y坐标 + (2 背包总列数) * 每格高
            ————————————————
            版权声明：本文为CSDN博主「weixin_39600837」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
            原文链接：https://blog.csdn.net/weixin_39600837/article/details/112610647
        '''
        
        self.setInitMousePos()

        bag_col = 8
           
        full_img = winApi.getGameImg()
        first_bag_center_pos = (self.box_head[0]+self.bag_width//2,self.box_head[1]+self.bag_height//2)
        
        # +0.4 像素来补正黑边
        bag_x = first_bag_center_pos[0] + int((cur_index % bag_col) * self.bag_width) 
        bag_y = first_bag_center_pos[1] + int((cur_index // bag_col) * self.bag_height)
        logger.debug('第一个背包位置:({},{})',bag_x,bag_y)

        cur_left = int(bag_x-self.bag_width/2)
        cur_right = int(bag_x+self.bag_width/2)
        cur_top = int(bag_y-self.bag_height/2)
        cur_bottom = int(bag_y+self.bag_height/2)

        a1_rect = Rectangle(cur_left-self.box_head[0],cur_top-self.box_head[1],cur_right-self.box_head[0],cur_bottom-self.box_head[1])
        # logger.debug('a1_rect:{}, rois:{}',a1_rect,rois)
        # 判断是否在bag中rois
        roi = self.containInROIs(a1_rect, rois)
        if roi is not None:
            logger.debug('当前点:{},{} 在区域{}中,修正装备截图所计算的坐标..',(cur_left,cur_top),(cur_right,cur_bottom),
                         (self.box_head[0]+roi.left, self.box_head[1]+roi.top, self.box_head[0]+roi.right, self.box_head[1]+roi.bottom))
            cur_left,cur_top,cur_right,cur_bottom = self.box_head[0]+roi.left, self.box_head[1]+roi.top, self.box_head[0]+roi.right, self.box_head[1]+roi.bottom
            logger.debug('修正后参数cur_left:{},cur_top:{},cur_right:{},cur_bottom:{}',cur_left,cur_top,cur_right,cur_bottom)
        else:
            logger.debug('当前点:{} 不在区域中',(cur_left,cur_top))
            return None    

        across_bag_img = full_img[cur_top:cur_bottom,cur_left:cur_right]
        
        # cv2.waitKey(0)

        
        rand_x = self.app_head[0]+bag_x+random.randint(-2,2)
        rand_y = self.app_head[1]+bag_y+random.randint(-1,1)
        logger.debug('移动到第{}格背包坐标:({},{})',bag_index,rand_x,rand_y)

        self.mouse.send_data_absolute(int(rand_x), int(rand_y))
        winApi.randomDelay(0.5,0.7)
        
        full_img = winApi.getGameImg()
        # 在背包外区域找当前装备的信息 459,525
        out_side_img = full_img[0:525,0:459]
        # cv2.imshow('out_side_img',out_side_img)
        # cv2.imshow('across_bag_img',across_bag_img)
        # cv2.waitKey(2000)
        findFlag,coordinate = find_one_picd(out_side_img,across_bag_img,0.9)
        
        equiq_img = None
        # 装备框右边界坐标
        
        if findFlag:
            logger.debug('找到装备信息框')
            # coordinate[2],coordinate[3] coordinate[2]+199,coordinate[3]+555
            equiq_img = full_img[coordinate[3]-7:coordinate[3]+554,coordinate[2]-3:coordinate[2]+201]

        if equiq_img is not None:
            logger.debug('查看装备等级信息...')
            findFlag, coordinate = find_one_picd(equiq_img,'startUI/img/dismant/equip_level.jpg',0.9)

            if findFlag:
                equiq_level_left,equiq_leveL_top,equiq_leveL_bottom = coordinate[2],coordinate[3],coordinate[-1]
                logger.debug('等级信息坐标equiq_level_left:{},equiq_leveL_top:{},equiq_leveL_bottom:{}',equiq_level_left,equiq_leveL_top,equiq_leveL_bottom)
                equiq_level_img = equiq_img[equiq_leveL_top:equiq_leveL_bottom+2,equiq_level_left:equiq_level_left+75]
                
                if equiq_level_img[0].shape[0] > 0:
                    equiq_level_img = cv2.cvtColor(equiq_level_img, cv2.COLOR_BGR2RGB)
                    # image = np.array(equiq_level_img)
                    image = self.imgPreprocessing(equiq_level_img)
                    # cv2.imshow('equiq_level_img',image)
                    # cv2.waitKey(2000)

                    equiq_level_txt = ocrUtil.detectImgOcrText(image,0)
                    
                    if equiq_level_txt is not None:
                        level_txts = ocrUtil.extract_numbers(equiq_level_txt)
                        logger.info('等级信息为:{}',level_txts[0])
                        if len(level_txts)>0:
                            return int(level_txts[0])
                        else:
                            return None
                else:
                    logger.warning('未识别到等级信息')
                    return None
        return None
    

if __name__ == '__main__':
    bag = Bag()
    rois = bag.find_bag_equipmentROI()
    bag.moveBagEquipmentGetLevel(1,rois)
