import os
import sys
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)

from config.cfg import *
import time
import pyautogui as pyautogui

'''
    定义一个适合ch9329的鼠标移动映射函数
'''
def custom_mouse_move_mapping(input_value):
    mappings = {
        0:0,
        1:0,
        2:0,
        3:2,
        4:3,
        5:4,
        6:5,
        7:6,
        8:7,
        9:8,
        10:10,
        11:12,
        12:15,
        13:16,
        14:19,
        15:21,
        16:23,
        17:25,
        18:28,
        19:29,
        20:32,
        21:34,
        22:36,
        23:38,
        24:41,
        25:42,
        26:45,
        27:46,
        28:49,
        29:51,
        30:54,
        31:55,
        32:58,
        33:59,
        34:62,
        35:64,
        36:66,
        37:68,
        38:70,
        39:73,
        40:74,
        41:77,
        42:79,
        43:81,
        44:84,
        45:85,
        46:88,
        47:89,
        48:92,
        49:94,
        50:95,
        51:98,
        52:101,
        53:102,
        54:105,
        55:107,
        56:109,
        57:111,
        58:114,
        59:115,
        60:117,
        61:120,
        62:122,
        63:124,
        64:126,
        65:128,
        66:131,
        67:133,
        68:133,
        69:137,
        70:140,
        71:141,
        72:143,
        73:146,
        74:148,
        75:149,
        76:152,
        77:154,
        78:156,
        79:159,
        80:161,
        81:162,
        82:165,
        83:167,
        84:170,
        85:171,
        86:174,
        87:175,
        88:178,
        89:180,
        90:182,
        91:184,
        92:185,
        93:189,
        94:191,
        95:193,
        96:195,
        97:196,
        98:199,
        99:202,
        100:204,
        101:205,
        102:207,
        103:210,
        104:213,
        105:214,
        106:217,
        107:218,
        108:221,
        109:223,
        110:225,
        111:227,
        112:229,
        113:232,
        114:233,
        115:235,
        116:238,
        117:240,
        118:243,
        119:244,
        120:246,
        121:249,
        122:251,
        123:252,
        124:255,
        125:258,
        126:259,
    }
    return mappings.get(input_value, "Invalid input")


screenwidth,screenheight = pyautogui.size()
print('screenwidth:',screenwidth,',screenheight:',screenheight)
# mouse.check_difference_ratio(960,540)

# mouse.send_data_absolute(1, 1)
# time.sleep(2)
# mouse.move_to(417, -399)
mouse.send_data_absolute(417, 399)

# mouse.move_to(417, -399)

time.sleep(1)
x_, y_ = pyautogui.position()
# 0.478760
print('x_:',x_,',y_:',y_)
# if x_-417>=20 or y_-399>=20:
#     print('绘制的曲线比例偏差过大')
#     file_path = os.path.join(os.getcwd(), 'corrector', 'information.json')
#     os.remove(file_path)
#     sys.exit(0)

# mouse.move_to(1022,-496)
# mouse.send_data_relatively(127,-127)
# time.sleep(1)
x_, y_ = pyautogui.position()
# 0.478760
print('x_:',x_,',y_:',y_)

# try_num = 127
# for i in range(try_num):
#     pre_x = x_
#     pre_y=y_
#     mouse.send_data_relatively(i,-i)
#     time.sleep(0.5)
#     x_, y_ = pyautogui.position()
#     if x_>=screenwidth-1 or y_>=screenheight-1:
#         # print('out of screen,reset')
#         mouse.send_data_absolute(1, 1)
#         pre_x = 1
#         pre_y=1
#         mouse.send_data_relatively(i,-i)
#         time.sleep(0.5)
#         x_, y_ = pyautogui.position()
#         # break
#     print(f'{i}:{(x_-pre_x)},')
    # print('i:',i,',x_:',x_,',y_:',y_)
    # print('ox_:',(x_-pre_x),',oy_:',(y_-pre_y))




# time.sleep(0.2)
# mouse.send_data_relatively(127,-127)
# time.sleep(0.2)
# mouse.send_data_relatively(127,-127)
# time.sleep(0.2)
# mouse.send_data_relatively(127,-112)
# time.sleep(0.2)
# mouse.send_data_relatively(127,0)
# time.sleep(0.2)
# mouse.send_data_relatively(127,0)
# time.sleep(0.2)
# mouse.send_data_relatively(127,0)
# time.sleep(0.2)
# mouse.send_data_relatively(126,0)

offex_x = 1022
offex_y = -496

my_ratio = 9

dis_offex_x = abs(offex_x)
dis_offex_y = abs(offex_y)
loop_x = offex_x / my_ratio
loop_y = offex_y / my_ratio
mod_x = offex_x % my_ratio
mod_y = offex_y % my_ratio
min_loop = int(min(abs(loop_x),abs(loop_y)))
max_loop = int(max(abs(loop_x),abs(loop_y)))
print(f'min_loop:{min_loop},max_loop:{max_loop},mod_x:{mod_x},,mod_y:{mod_y}')
dir = [0,0]
for i in range(min_loop): 
    if loop_x > 0:
        dir[0] = my_ratio
        dis_offex_x -= my_ratio
    elif loop_x < 0:
        dir[0] = -my_ratio
        dis_offex_x -= my_ratio
    if loop_y > 0:
        dir[1] = my_ratio
        dis_offex_y -= my_ratio
    elif loop_y < 0:
        dir[1] = -my_ratio
        dis_offex_y -= my_ratio
    print('i:',i,',dir相对移动：',dir[0],',',dir[1]) 
    print('i:',i,',curr_offex_x:',dis_offex_x,',curr_offex_y:',dis_offex_y)
    mouse.send_data_relatively(dir[0],dir[1])
    time.sleep(0.006)

dir = [0,0]
# 与目标点x轴距离小于阈值，只移动y轴坐标
if dis_offex_x < my_ratio:
    for i in range(max_loop-min_loop):
        if loop_y > 0 and abs(dis_offex_y) >= my_ratio:
            dir[1] = my_ratio
            dis_offex_y -= my_ratio
        elif loop_y < 0 and abs(dis_offex_y) >= my_ratio:
            dir[1] = -my_ratio
            dis_offex_y -= my_ratio
        print('i:',i,',y相对移动：',0,',',dir[1]) 
        mouse.send_data_relatively(0,dir[1])
        time.sleep(0.006)
# 与目标点y轴距离小于阈值，只移动x轴坐标
if dis_offex_y < my_ratio:
    for i in range(max_loop-min_loop):
        if loop_x > 0 and abs(dis_offex_x) >= my_ratio:
            dir[0] = my_ratio
            dis_offex_x -= my_ratio
        elif loop_x < 0 and abs(dis_offex_x) >= my_ratio:
            dir[0] = -my_ratio
            dis_offex_x -= my_ratio
        print('i:',i,',x相对移动：',dir[0],',',0) 
        mouse.send_data_relatively(dir[0],0)
        time.sleep(0.006)
    
time.sleep(1)           
mouse.send_data_relatively(mod_x*int(offex_x/abs(offex_x)),mod_y*int(offex_y/abs(offex_y)))