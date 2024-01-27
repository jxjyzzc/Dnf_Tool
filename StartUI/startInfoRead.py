import os
import sys
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)

from gameUtils.recognition.Rectangle import Rectangle
from tool.ocrutil import cv_imread,cv_imread_roi,find_one_picd,find_multiple_picd
from tool.ocrutil import ocrUtil
import cv2
import numpy as np
import random

"""
    去除图片背景
""" 
def remove_background(background,img):
    diff = cv2.absdiff(background, img)
    return diff

# 查看当前选择的角色框截图
def find_curr_role_picd(img: str):
    cur_img = None

    # roi_img = cv_imread_roi(img_path, offer_left, offer_top, offer_right, offer_bottom)
    isCurr,coordinate = find_one_picd(img,'startUI/img/cur_pic.jpg',0.7)
    # 当前角色坐标
    if isCurr:
        # left,top,right,bottom
        (curr_left,curr_bottom) = (coordinate[2],coordinate[5])
        curr_top = curr_bottom - 49-random.randint(-2,2)
        curr_right = curr_left + 130+random.randint(-2,2)
        # print('当前角色左下角起始点:',(curr_left,curr_bottom))
        # print('当前角色矩形坐标:',(curr_left,curr_top,curr_right,curr_bottom))

        cur_img = cv_imread_roi(img,curr_left,curr_top,curr_right,curr_bottom)
        # cv2.imshow('pre_cur_img', cur_img)
        # cv2.waitKey(0)
        bg = cv_imread_roi('startUI/img/rolebackgroud.jpg', curr_left, curr_top, curr_right, curr_bottom)
        # print(f'cur_img shape:{cur_img.shape},bg shape:{bg.shape}')
        # 假设 cur_img 是一个 4 通道的 numpy 数组
        if cur_img.shape[2] == 4:  # 检查是否有 4 个通道
            cur_img = cv2.cvtColor(cur_img, cv2.COLOR_RGBA2BGR)  # 将 RGBA 转换为 BGR
        cur_img = remove_background(bg,cur_img)
        # cv2.imshow('after_cur_img', cur_img)
        # cv2.waitKey(2000)
        return cur_img,(curr_left,curr_top,curr_right,curr_bottom)
    return None,None

# 读取当前选择的角色信息
def read_curr_role_info(img: str):
    cur_img,cur_roi = find_curr_role_picd(img)
    if cur_img is None:
        return []
    # print('cur_img',cur_img)
    # 截取图片进行识别
    tmp_jpg_path = 'tmp.jpg'
    cv2.imwrite(tmp_jpg_path,cur_img)
    image = np.array(cur_img)

    # cv2.imshow('cur_img', image)
    # cv2.waitKey(2000)
    # cv2.destroyAllWindows()
    result = ocrUtil.detectImgOcr(image)

    new_result = []

    print('read_curr_role_info result:',result)
    print('read_curr_role_info result size:',len(result[0]))
    if len(result[0]) < 2:
        return new_result

    boxes = [detection[0] for line in result for detection in line]
    txts = [detection[1][0] for line in result for detection in line] 
    text1 = txts[0].replace('级',' ')
    text3 = txts[-1].replace(',', '').replace('.', '').replace('，','')
    txts = [text1,txts[1],text3]

    
    # 开始界面人物信息只有3行
    if len(result[0])>=3:
        for i in range(len(boxes)):
            if txts[i] != '':
                new_result.append((cur_roi,txts[i]))

    # os.remove(tmp_jpg_path)
    return new_result

"""判断是否是在角色选择界面"""
def isInStart(img):
    isStart,coordinate = find_one_picd(img,'startUI/img/start_game.jpg',0.9)
    return isStart

def is_integer_instance(s):
    try:
        num = int(s)
        return isinstance(num, int)
    except ValueError:
        return False

"""
    开始游戏界面信息读取
"""    
def startGameInfo(max_img,job_img='startUI/img/job_list/阿修罗.jpg'):
    job_postion_list = []
    # bg = cv_imread('startUI/img/rolebackgroud.jpg')
    # remove_bg_img = remove_background(bg,max_img)
    # cv2.imshow('remove_bg_img', remove_bg_img)
    # cv2.waitKey(0)
    coordinates = find_multiple_picd(max_img,job_img,0.8)
    # isStart,coordinate = self.find_one_picd('test/img/角色选择.jpg',job_img,0.8)
    # isStart,coordinate = find_picd('test/img/角色选择.jpg','StartUI/img/start_game.jpg',0.8)
    if coordinates is not None and len(coordinates) > 0:
        for coordinate in coordinates:
            # print('找到职业图片坐标:',list(coordinate[0]),list(coordinate[1]))
            # cv_imread_roi('test/img/角色选择.jpg',[[81.0, 272.0], [152.0, 272.0], [152.0, 289.0], [81.0, 289.0]])
            left,top,right,bottom = (coordinate[0][0]-30,coordinate[0][1]-20,coordinate[1][0]+30,coordinate[1][1]+20)
            tmp_img =  cv_imread_roi(max_img,left,top,right,bottom)
            # 假设 cur_img 是一个 4 通道的 numpy 数组
            if tmp_img.shape[2] == 4:  # 检查是否有 4 个通道
                tmp_img = cv2.cvtColor(tmp_img, cv2.COLOR_RGBA2BGR)  # 将 RGBA 转换为 BGR
            bg = cv_imread_roi('startUI/img/rolebackgroud.jpg', left, top, right, bottom)
            tmp_img = remove_background(bg,tmp_img)
            # cv2.imshow('tmp_img', tmp_img)
            # cv2.waitKey(0)
            
            texts = ocrUtil.detectImgOcrText(tmp_img)
            print('texts:',texts)
            # text1 = None
            if len(texts)<2:
                continue
            # elif len(texts)==3:
            #     text1 = texts[0].replace('级',' ')
            # elif len(texts)==4:
            #     text1 = (texts[0]+texts[1]).replace('级',' ')    
            text3 = texts[-1].replace(',', '').replace('.', '').replace('，','')
            # print('text:',text1,'text3:',text3)
            # 名字不能精准识别，放弃对人物名称识别了
            # if '110' in text1 and int(text3) > 35000:
                # job_postion_list.append(([left,top,right,bottom],text1))
            if text3 is not None and is_integer_instance(text3) and int(text3) > 35000:
                job_postion_list.append(([left,top,right,bottom],text3))
    return job_postion_list        

if __name__ == '__main__':
    full_img = cv_imread('test/img/角色选择1.jpg')
    # job_postion_list = startGameInfo(full_img)
    # print('job_postion_list:',job_postion_list)
    # for job_postion in job_postion_list:
    #     roi_img = cv_imread_roi(full_img,job_postion[0][1],job_postion[0][1],job_postion[0][2],job_postion[0][3])
    #     cv2.imshow('roi_img', roi_img)
    #     cv2.waitKey(2000)

    inStart = isInStart(full_img)
    print('inStart:',inStart)

    # for i in range(1,8):
    #     img_path = 'test/img/roleSelect{i}.jpg'.format(i=i)
    #     print('img_path:',img_path)
    #     result=read_curr_role_info(img_path)
    #     print('result:',result)

## [[[[19.0, 167.0], [113.0, 167.0], [113.0, 183.0], [19.0, 183.0]], ('110级刷图看少情', 0.8676621317863464)], [[[33.0, 182.0], [100.0, 182.0], [100.0, 195.0], [33.0, 195.0]], ('极谐阿修罗', 0.9840165972709656)], [[[43.0, 196.0], [88.0, 198.0], [88.0, 208.0], [42.0, 206.0]], ('41.119', 0.9844369888305664)]]
    