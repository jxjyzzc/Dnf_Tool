# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 09:45:04 2020

@author: analoganddigital   ( GitHub )
"""

import os
import time

import cv2
import numpy as np
import getkeys
import grabscreen

wait_time = 5
L_t = 3
save_step = 200
# file_name = 'training_data_2_3.npy'
data_path = 'd:/datasets/dnf/grabs/'
os.makedirs(data_path, exist_ok=True)
# window_size = (0,0,1920,1080)#384,344  192,172 96,86
window_size = None

# if os.path.isfile(file_name):
#     print("file exists , loading previous data")
#     training_data = list(np.load(file_name,allow_pickle=True))
# else:
#     print("file don't exists , create new one")
#     training_data = []

training_data = []
save = True
for i in list(range(wait_time))[::-1]:
    print(i+1)
    time.sleep(1)

last_time = time.time()
counter = 0

org_num = len(os.listdir(data_path))
while(True):
    output_key = getkeys.get_key(getkeys.key_check()) #按键收集
    # p键保存
    if output_key == 100:
        if save:
            print(len(training_data) + counter*save_step)
            for i, d in enumerate(training_data):
                file_name = os.path.join(data_path, str(org_num + counter*save_step + i) + "_" + str(d[1]) + '.jpg')
                cv2.imwrite(file_name, d[0])
            print("save finish")
        break

    game_screenshot = grabscreen.grab_screen('地下城与勇士：创新世纪',window_size)
    if game_screenshot is None:
        break

    screen_gray = cv2.cvtColor(game_screenshot,cv2.COLOR_BGRA2BGR)#灰度图像收集
    old_tuple = screen_gray.shape[:2]
    # 约定分辨率 800,600
    new_tuple = (800,600)
    screen_reshape = screen_gray
    #判断图片是否需要缩放
    if np.array_equal(old_tuple, new_tuple):
        screen_reshape = cv2.resize(screen_gray,new_tuple) # 1200, 750   600, 375

    training_data.append([screen_reshape,output_key])

    if len(training_data) % save_step == 0 and save:
        print('training_data len:',len(training_data))
        for i, d in enumerate(training_data):
            file_name = os.path.join(data_path, str(org_num + counter*save_step + i) + "_" + str(d[1]) + '.jpg')
            cv2.imwrite(file_name, d[0])
        training_data.clear()
        counter += 1
    cv2.imshow('image_grab window',screen_reshape)

    #测试时间用
    print('每帧用时 {} 秒'.format(time.time()-last_time))
    print("瞬时fps：", 1/(time.time()-last_time))
    last_time = time.time()

    # 等待按下Esc退出
    if cv2.waitKey(1000) == 27:
        break
print('采集图片结束，按任意键退出')    
cv2.waitKey()# 视频结束后，按任意键退出
cv2.destroyAllWindows()
