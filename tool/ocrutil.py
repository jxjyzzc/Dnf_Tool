
import cv2
import numpy as np
from loguru import logger
import time,os
import re

#读取图像，解决imread不能读取中文路径路径的问题
def cv_imread(file_path):
    cv_img = None
    #imdedcode读取的是RGB图像
    with open(file_path, 'rb') as f:
        data = f.read()
        cv_img = cv2.imdecode(np.frombuffer(data,dtype=np.uint8),-1)
    return cv_img

 #读取选定区域截图信息
def cv_imread_roi(file_img,left: float,top: float,right: float,bottom: float):
    if isinstance(file_img,str):
        full_img = cv_imread(file_img)
    elif isinstance(file_img, np.ndarray):
        full_img = file_img
    
    cropped = full_img[top:bottom, left:right]
    # cv2.imshow("card",cropped)
    # cv2.imshow("full_img",full_img)
    # cv2.waitKey(0)   #延时显示，0代表无限延时
    return cropped

'''
    从截图中查找图片坐标
    @param img: 截图路径/图片nparray
    @param findimg_path: 要查找的图片路径
    @param threshold: 阈值，0-1之间，0表示完全不匹配，1表示完全匹配
    @return: 匹配成功返回True, 匹配失败返回False, 
        匹配坐标 前2个参数为中心点坐标,后面4个参数为 left,top,right,bottom

'''
def find_one_picd(max_img, find_img: str, threshold: float):
    threshold = 1-threshold
    if isinstance(max_img,str):
        scr = cv_imread(max_img)
    elif isinstance(max_img, np.ndarray):
        scr = max_img
    if isinstance(find_img,str):
        tp = cv_imread(find_img)
    elif isinstance(max_img, np.ndarray):
        tp = find_img    
    try:
        result = cv2.matchTemplate(scr, tp, cv2.TM_SQDIFF_NORMED)
    except cv2.error as e:
        # print('出错文件:{},出错行号:{},msg:{}'.format(e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno,e.msg))
        # 实时不明原因失败处理
        max_path = 'test/img/max_img_error.jpg'
        min_path = 'test/img/min_img_error.jpg'
        cv2.imwrite(max_path, scr)
        cv2.imwrite(min_path, tp)
        try:
            # result = cv2.matchTemplate(scr, tp, cv2.TM_SQDIFF_NORMED)
            result = cv2.matchTemplate(cv_imread(max_path), cv_imread(min_path), cv2.TM_SQDIFF_NORMED)
            os.remove(max_path)
            os.remove(min_path)
        except cv2.error as e:
            logger.error('出错文件:{},出错行号:{},msg:{}',e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno,e.msg)
            return False, None
    # h, w = scr.shape[:2]
    h, w = tp.shape[:2]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if min_val > threshold:
        # os.remove("im_opencv.jpg")
        return False, None
    else:
        coordinate=(int(min_loc[0]+w/2), int(min_loc[1]+h/2), int(min_loc[0]), int(min_loc[1]), int(min_loc[0]+w), int(min_loc[1]+h))
        # print(max_img, min_val, min_loc)
        # print('find_one_picd 左上角坐标值:',min_loc[0],min_loc[1])
        # os.remove("im_opencv.jpg")
        return True, coordinate

# 多模版匹配
def find_multiple_picd( img, findimg, threshold: float):
    coordinates = []
    if isinstance(img,str):
        img_rgb  = cv_imread(img)
    elif isinstance(img, np.ndarray):
        img_rgb = img
    if isinstance(findimg,str):
        template  = cv_imread(findimg)
    elif isinstance(findimg, np.ndarray):
        template = findimg        
    
    h, w = template.shape[:2]

    try:
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    except cv2.error as e:
        # print('出错文件:{},出错行号:{},msg:{}'.format(e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno,e.msg))
        # 实时不明原因失败处理
        max_path = 'test/img/max_img_error.jpg'
        min_path = 'test/img/min_img_error.jpg'
        cv2.imwrite(max_path, img_rgb)
        cv2.imwrite(min_path, template)
        try:
            res = cv2.matchTemplate(cv_imread(max_path), cv_imread(min_path), cv2.TM_CCOEFF_NORMED)
            os.remove(max_path)
            os.remove(min_path)
        except cv2.error as e:
            logger.error('出错文件:{},出错行号:{},msg:{}',e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno,e.msg)
            return False, None
        
    # threshold = 0.8
    # 取匹配程度大于%80的坐标
    loc = np.where(res >= threshold)

    for pt in zip(*loc[::-1]):  # *号表示可选参数
        top_left = int(pt[0]), int(pt[1])
        bottom_right = (int(pt[0] + w), int(pt[1] + h))
        # cv2.rectangle(img_rgb, pt, bottom_right, (0, 0, 255), 2)
        coordinates.append((top_left, bottom_right))
    # cv2.imshow('img_rgb', img_rgb)
    # cv2.waitKey(0)
    return coordinates

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image

class OcrUtil:

    def __init__(self):
        
        # 设置重试策略
        retry_strategy = Retry(
            total=5,
            backoff_factor=0.1,
            status_forcelist=[ 500, 502, 503, 504 ],
            method_whitelist=["HEAD", "GET", "POST", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)


        self.ocr_req_url = 'http://127.0.0.1:5000/ocr/paddleocr'
        self.ocr_req = requests.Session()
        self.ocr_req.mount("http://", adapter)
        self.ocr_req.mount("https://", adapter)
        return



    '''
        图片识别为ocr文字
        img_path: 图片路径
        return: ocr 位置信息，文本，置信率
    '''    
    def detectImgOcr(self, img):
        img_file_path = 'data/tmp_ocr.png'
        im_PIL = Image.fromarray(img)
        # profile = ImageCms.createProfile("sRGB")
        im_PIL.save(img_file_path)
        # im_PIL.show()

        files = {'image': open(img_file_path, 'rb')}
        response = self.ocr_req.post(self.ocr_req_url,files=files)
        status_code = response.status_code
        if status_code == 200:
            result = response.json()['data']
        else:
            result = []   
        logger.debug('result:{},status_code:{}',result,status_code)
        # for line in result:
        #     print(line)
        
        # 显示结果
        # from PIL import Image
        # image = Image.open(img).convert('RGB')
        # boxes = [detection[0] for line in result for detection in line]  # Nested loop added
        # txts = [detection[1][0] for line in result for detection in line]  # Nested loop added
        # scores = [detection[1][1] for line in result for detection in line]  # Nested loop added


        # print('boxes:',boxes)
        # print('txts:',txts)
        # print('scores:',scores)

        # im_show = draw_ocr(image, boxes, txts, scores, font_path='ocr/simfang.ttf')
        # im_show = Image.fromarray(im_show)
        # im_show.save('result.jpg')

        return result

    '''
        图片识别为ocr文字
        img: 图片
        line_num: 要识别的行号
        return: ocr文本
    '''    
    def detectImgOcrText(self, img,line_num:int=None):
        img_file_path = 'data/tmp_ocr.png'
        cv2.imwrite(img_file_path,img)
        files = {'image': open(img_file_path, 'rb')}
        response = self.ocr_req.post(self.ocr_req_url,files=files)
        status_code = response.status_code
        if status_code == 200:
            result = response.json()['data']
        else:
            result = []
        logger.debug('result:{},status_code:{}',result,status_code)

        if len(result[0])<0:
            return []

        txts = [detection[1][0] for line in result for detection in line]
        if line_num is None:
            return txts
        else:
            return txts[line_num] if len(txts)>0 else None
       
 
    """
        提取文本中数字
    """
    def extract_numbers(self,text):
        pattern = r'\d+'  # 匹配一个或多个连续的数字字符
        num_list = re.findall(pattern, text)
        return num_list

ocrUtil = OcrUtil()    

if __name__ == '__main__':
    # print(ocrUtil.detectImgOcr('test/img/detect_error.jpg'))
    print(find_one_picd('test/img/max_img_error.jpg','test/img/min_img_error.jpg',0.8))
    # print('ocr')