import os
import sys
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)

# from tool.ocrutil import ocrUtil
import cv2
import numpy as np
import gameUtils.app as app
from gameUtils.WindowsAPI import winApi
import time

# def getRoleInfo(img_path: str):
    


if __name__=="__main__":
    handle, app_head, app_tail, app_width, app_height = app.find_app('地下城与勇士：创新世纪')
    hwnd = winApi.getHwnd()
    full_img = winApi.getGameImg()
    level_img = full_img[586:600,197:240]
    cv2.imshow("level_img",level_img)
    
    # map_img = ocrUtil.cv_imread_roi(full_img, 663,29,783,48)
    map_img = full_img[29:48,663:783]
    cv2.imshow("map_img",map_img)
    # 激活窗口
    winApi.showWindow()
    game_x = 730
    game_y = -592
    print("窗口左上角坐标:",app_head)
    time.sleep(0.5)
    winApi.moveAbs(app_head[0]+abs(game_x)-1, app_head[1]+abs(game_y)+1)
    winApi.moveAbs(app_head[0]+abs(game_x), app_head[1]+abs(game_y))
    time.sleep(1.5)
    full_img = winApi.getGameImg() 
    power_img = full_img[575:586,696:787]
    cv2.imshow("power_img",power_img)

    cv2.waitKey(0)   #延时显示，0代表无限延时