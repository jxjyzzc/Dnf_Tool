import os
import sys
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)

from gameUtils.recognition.Rectangle import RecRectangle as rec_rectangle
from tool.ocrutil import ocrUtil
import cv2


# 查看当前选择的角色框截图
def find_curr_role_picd(img_path: str):
    cur_img = None
    # 截取角色区域范围，避免干扰
    offer_left = 0
    offer_top = 85
    offer_right = 777
    offer_bottom = 546
    
    
    roi_img = ocrUtil.cv_imread_roi(img_path, offer_left, offer_top, offer_right, offer_bottom)
    isCurr,coordinate = ocrUtil.find_one_picd(img_path,'startUI/img/cur_pic.jpg',0.8)
    # 当前角色坐标
    if isCurr:
        # left,top,right,bottom
        (curr_left,curr_bottom) = (coordinate[2],coordinate[5])
        curr_top = curr_bottom - 217
        curr_right = curr_left + 135
        print('当前角色左下角起始点:',(curr_left,curr_bottom))
        print('当前角色矩形坐标:',(curr_left,curr_top,curr_right,curr_bottom))

        cur_img = ocrUtil.cv_imread_roi(img_path,curr_left,curr_top,curr_right,curr_bottom)
        bg = ocrUtil.cv_imread_roi('startUI/img/rolebackgroud.jpg', curr_left, curr_top, curr_right, curr_bottom)
        rec_rect = rec_rectangle(bg)
        cur_img = rec_rect.remove_background(cur_img)
        # cv2.imshow('cur_img', cur_img)
        # cv2.waitKey(0)
    # cur_role_points = rec_rect.rectangle_recognition(roi_img)
    # if len(cur_role_points) == 4:
    #     # 提取每个矩形的坐标
    #     left = min(cur_role_points, key=lambda x: x[0])[0] + offer_left
    #     top = min(cur_role_points, key=lambda x: x[1])[1]+ offer_top
    #     bottom = max(cur_role_points, key=lambda x: x[1])[1] + offer_top
    #     right = max(cur_role_points, key=lambda x: x[0])[0] + offer_left
    #     print(f"left: {left}, top: {top}, bottom: {bottom}, right: {right}")

    #     cur_img = cv_imread_roi(img_path, int(left), int(top), int(right), int(bottom))

    #     cv2.imshow('cur_img', cur_img)
    #     cv2.waitKey(0)

    return cur_img

# 读取当前选择的角色信息
def read_curr_role_info( img_path: str):
    cur_img = find_curr_role_picd(img_path)

    # 截取图片进行识别
    tmp_jpg_path = 'tmp.jpg'
    cv2.imwrite(tmp_jpg_path,cur_img)
    ocrUtil.detectImgOcr(tmp_jpg_path)
    os.remove(tmp_jpg_path)
            
    
def isStartGame(self, job_img_path='test/img/阿修罗.jpg'):
    isStart,coordinate = self.find_one_picd('test/img/角色选择.jpg',job_img_path,0.8)
    # isStart,coordinate = find_picd('test/img/角色选择.jpg','StartUI/img/start_game.jpg',0.8)
    if isStart:
            print('找到职业图片坐标:',coordinate[2:])
            # cv_imread_roi('test/img/角色选择.jpg',[[81.0, 272.0], [152.0, 272.0], [152.0, 289.0], [81.0, 289.0]])
            left,top,right,bottom = list(coordinate[2:])
            tmp_img =  self.cv_imread_roi('test/img/角色选择.jpg',left,top,right,bottom)
            # 截取图片进行识别
            tmp_jpg_path = 'tmp.jpg'
            cv2.imwrite(tmp_jpg_path,tmp_img)
            self.detectImg(tmp_jpg_path)
            os.remove(tmp_jpg_path)
    return isStart        

if __name__ == '__main__':
    # isStartGame('test/img/名望图片.jpg')
    # find_multiple_picd('test/img/roleSelect4.jpg','test/img/阿修罗.jpg',0.8)
    for i in range(1,8):
        img_path = 'test/img/roleSelect{i}.jpg'.format(i=i)
        print('img_path:',img_path)
        read_curr_role_info(img_path)

## [[[[19.0, 167.0], [113.0, 167.0], [113.0, 183.0], [19.0, 183.0]], ('110级刷图看少情', 0.8676621317863464)], [[[33.0, 182.0], [100.0, 182.0], [100.0, 195.0], [33.0, 195.0]], ('极谐阿修罗', 0.9840165972709656)], [[[43.0, 196.0], [88.0, 198.0], [88.0, 208.0], [42.0, 206.0]], ('41.119', 0.9844369888305664)]]
    