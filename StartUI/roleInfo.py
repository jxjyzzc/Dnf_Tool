import os,sys
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
## parenddir 是当前代码文件所在目录的父目录
parenddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parenddir)

from startUI import Bag,startInfoRead

from gameUtils.GameInfo import GAMEINFO 
from gameUtils import SIFTLoc as siftLoc,app as app
from gameUtils.WindowsAPI import winApi
from tool.ocrutil import cv_imread,find_one_picd,cv_imread_roi
from tool.ocrutil import ocrUtil
import cv2
import numpy as np

import time,random
from loguru import logger


class RoleInfo():

    """
        角色信息类
        bag_max_row: 背包行数最大值
        dismant_highest_level: 可分解装备做高等级
    """
    def __init__(self):
        # 键盘操作接口
        self.keyboard = winApi.getKeyboard()
        self.mouse = winApi.getMouse()
        handle, app_head, app_tail, app_width, app_height = app.find_app('地下城与勇士：创新世纪')
        GAMEINFO.gameHwnd = winApi.getHwnd()
        GAMEINFO.gameRect = {"x":app_head[0],"y":app_head[1],"width":app_width,"height":app_height}
        self.app_head = app_head  
        pass

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
    def getBasicRoleInfo(self):
        roleResult = {}
        
        full_img = winApi.getGameImg()
        level_img = full_img[586:600,197:240]
        image = self.imgPreprocessing(level_img)
        
        # cv2.imshow("level_img",image)
        # cv2.waitKey(0)
        # cv2.imwrite('test/img/level.jpg',image)

        result = ocrUtil.detectImgOcr(image)
        roleResult['level'] = [detection[1][0] for line in result for detection in line]
        if  len(roleResult['level'])>0:
            roleResult['level'] = roleResult['level'][0]
        # print('level:',result)

        map_img = full_img[29:48,663:783]

        image = self.imgPreprocessing(map_img)
        # cv2.imshow("map_img",image)
        # cv2.waitKey(0)

        result = ocrUtil.detectImgOcr(image)
        roleResult['map'] = [detection[1][0] for line in result for detection in line]
        if  len(roleResult['map'])>0:
            roleResult['map'] = roleResult['map'][0]
        # print('map:',result)

        # 激活窗口
        winApi.showWindow()
        # 移动到疲劳值位置
        game_x = 730
        game_y = -592
        # print("窗口左上角坐标:",app_head)
        time.sleep(0.5)
        self.mouse.send_data_absolute(self.app_head[0]+abs(game_x)-1, self.app_head[1]+abs(game_y)+1)
        time.sleep(0.2)
        self.mouse.send_data_absolute(self.app_head[0]+abs(game_x), self.app_head[1]+abs(game_y))
        time.sleep(1.5)
        full_img = winApi.getGameImg() 
        power_img = full_img[572:590,696:789]

        image = self.imgPreprocessing(power_img)
        # cv2.imwrite('test/img/power.jpg',image)
        # cv2.imshow("power_img",image)
        # cv2.waitKey(0)   #延时显示，0代表无限延时

        result = ocrUtil.detectImgOcr(image)
        roleResult['power'] = [detection[1][0][4:] for line in result for detection in line]
        if  len(roleResult['power'])>0:
            roleResult['power'] = roleResult['power'][0]
        # print('power:',result)
        return roleResult

    """
        切换角色
    """
    def changeRole(self):
        jobList = GAMEINFO.joblist
        logger.info('开始切换角色。。。')
        full_img = winApi.getGameImg()
        winApi.randomDelay(0.3,0.5)

        # 判断是否在选择角色界面 
        job_postion_list = startInfoRead.startGameInfo(full_img)
        esc_press = False
        if len(job_postion_list)== 0: 
           esc_press = True
        
        if esc_press:
            logger.debug('未在选择角色界面，esc尝试进入')
            find_select_role,coordinate = find_one_picd(full_img,'startUI/img/select_role.jpg',0.9)
            while not find_select_role:
                winApi.keyDown('ES')
                winApi.randomDelay(1.3,1.5)
                full_img = winApi.getGameImg()
                winApi.randomDelay(0.3,0.5)
                find_select_role,coordinate = find_one_picd(full_img,'startUI/img/select_role.jpg',0.9)
                if find_select_role:
                    logger.debug('选择角色按钮坐标：{}',(GAMEINFO.gameRect['x']+coordinate[0],GAMEINFO.gameRect['y']+coordinate[1]))
                    winApi.moveAbsClick(GAMEINFO.gameRect['x']+coordinate[0]+random.randint(-5,5), GAMEINFO.gameRect['y']+coordinate[1]+random.randint(-22,2))
                    time.sleep(2.5)
                    full_img = winApi.getGameImg()
                    # cv2.imshow('full_img',full_img)
                    # cv2.waitKey(0)
        
        if len(job_postion_list) == 0:        
            job_postion_list = startInfoRead.startGameInfo(full_img)
        # logger.debug('job_postion_list:{}',job_postion_list)

        tryCount = 0 
        # 切换角色需要排除当前选中角色
        while tryCount < 10:
            cur_res =startInfoRead.read_curr_role_info(full_img)
            if len(cur_res)>0:
                tryCount = 0
                break
            tryCount+=1
            time.sleep(2)
        # print('cur_res:',cur_res)

        if len(jobList)>0:
            
            cur_role = cur_res[0][-1]
            # 获取要切换的角色
            for job in job_postion_list:
                if job[-1] != cur_role:
                    next_role = job[1]
                    print('job:',job)
                    job_x,job_top,job_right,job_bottom = GAMEINFO.gameRect['x']+job[0][0],GAMEINFO.gameRect['y']+job[0][1],GAMEINFO.gameRect['x']+job[0][2],GAMEINFO.gameRect['y']+job[0][3]
                    job_center_x = int((job_x+job_right)/2)
                    job_center_y = int((job_top+job_bottom)/2)
                    logger.debug('找到要切换的角色 {} 坐标：{}，{}，{},{}'.format(next_role,job_x,job_top,job_right,job_bottom))
                    winApi.moveAbsClick(job_center_x+random.randint(-5,5), job_center_y+random.randint(-22,2))
                    winApi.randomDelay(0.3,0.5)
                    winApi.keyDown('SP')
                    winApi.randomDelay(1.3,1.5)
                    logger.info('完成角色切换: {} --> {}',cur_role,next_role)
                    return cur_role,next_role

        return None,None

    """
        分解装备
    """
    def dismantlingEquipment(self):
        logger.info('开始分解装备。。。')
        winApi.keyDown(",,")
        winApi.randomDelay(0.3,0.5)
        rand_x = GAMEINFO.gameRect['x']+random.randint(380,432)
        rand_y = GAMEINFO.gameRect['y']+random.randint(330,341)
        winApi.moveAbsClick(rand_x, rand_y)
        winApi.keyDown("AA")
        winApi.randomDelay(0.3,0.5)
        
        full_img = winApi.getGameImg()
        findFlag,coordinate = find_one_picd(full_img,'startUI/img/dismant/un_dismant.jpg',0.7)
        if findFlag:
            logger.info('缺少要分解的物品！！！')
        else:
            logger.info('开始分解。。。')
            winApi.keyDown("SP")
            winApi.randomDelay(3.3,5.5)

        winApi.keyDown("ES")
        winApi.randomDelay(0.3,0.5)

        logger.info('。。。副职业分解装备完毕')
        full_img = winApi.getGameImg()
        winApi.randomDelay(0.3,0.5)
        # cv2.imshow('full_img',full_img)
        # cv2.waitKey(2000)
        next_flag = False
        findFlag,coordinate = find_one_picd(full_img,'startUI/img/dismant/dismantEquip.jpg',0.7)
        if findFlag:
            logger.info('找到分解机。。。')
            rand_x = GAMEINFO.gameRect['x']+int(coordinate[0])+random.randint(0,5)
            rand_y = GAMEINFO.gameRect['y']+int(coordinate[1])+random.randint(15,20)
            winApi.moveAbsClick(rand_x, rand_y)
            winApi.randomDelay(0.5,0.8)
            next_flag = True
        else:
            logger.warning('。。。未找到分解机')
            next_flag = False    

        if next_flag:
            full_img = winApi.getGameImg()
            findFlag,coordinate = find_one_picd(full_img,'startUI/img/dismant/dismantEquip_select.jpg',0.7)
            # 点击分解装备
            if findFlag:
                rand_x = GAMEINFO.gameRect['x']+int(coordinate[0])+random.randint(5,8)
                rand_y = GAMEINFO.gameRect['y']+int(coordinate[1])+random.randint(5,8)
                logger.info(f'点击分解装备,x:{rand_x},y:{rand_y}')
                winApi.moveAbsClick(rand_x, rand_y)
                winApi.randomDelay(0.5,0.8)
            else:    
                next_flag = False
        
        if next_flag:
            bag = Bag()
            logger.info('开始查看装备栏信息,当前角色共有{}行装备需要遍历..',bag.bag_max_row)
            rois = bag.find_bag_equipmentROI()
            for i in range(0,bag.bag_max_row): 
                # 整行为空格数
                row_empty_num = 0
                for j in range(1,9):
                    # 有一排空格，认为已经空了，不需要再遍历了
                    if row_empty_num>= 8:
                        break
                    cur_level_num = bag.moveBagEquipmentGetLevel(i*8+j,rois)
                    if cur_level_num is None:
                        row_empty_num += 1
                        continue
                    if cur_level_num < bag.dismant_highest_level:
                        logger.info(f'第{i+1}行第{j}个装备放入分解机...')
                        self.mouse.click()
                        winApi.randomDelay(0.2,0.4)
                        row_empty_num = 0
            logger.info('遍历完毕，开始分解...')
            # 分解按钮 326,407
            
            full_img = winApi.getGameImg()
            findFlag,coordinate = find_one_picd(full_img, 'startUI/img/dismant/dismant_button.jpg', 0.8)
            if findFlag:
                custom_x = GAMEINFO.gameRect['x']+int(coordinate[0])
                custom_y = GAMEINFO.gameRect['y']+int(coordinate[1])
                logger.info(f'分解按钮,x:{custom_x},y:{custom_y}')
                winApi.moveAbsClick(custom_x, custom_y)
                time.sleep(0.5)
            
            full_img = winApi.getGameImg()
            findFlag,coordinate = find_one_picd(full_img, 'startUI/img/dismant/dismantEquip_checkbox.jpg', 0.8)
            if findFlag:
                custom_x = GAMEINFO.gameRect['x']+int(coordinate[0])
                custom_y = GAMEINFO.gameRect['y']+int(coordinate[1])
                logger.info(f'自定义确认装备按钮,x:{custom_x},y:{custom_y}')
                winApi.moveAbsClick(custom_x, custom_y)
                time.sleep(0.5)

            full_img = winApi.getGameImg()
            findFlag,coordinate = find_one_picd(full_img, 'startUI/img/confirm_button.jpg', 0.8)
            if findFlag:
                rand_x = GAMEINFO.gameRect['x']+int(coordinate[0])+random.randint(5,8)
                rand_y = GAMEINFO.gameRect['y']+int(coordinate[1])+random.randint(5,8)
                logger.info(f'点击分解确认按钮,x:{rand_x},y:{rand_y}')
                winApi.moveAbsClick(rand_x, rand_y)
                time.sleep(3.5)
                winApi.keyDown('ES')
                
                logger.info('============分解完成===========')
        return
    
    
    
    '''
        判断角色是否在推荐地图中,截图中有“频道”代表在城镇中
        返回值: True/False
    '''
    def isInRecommendMap(self,im_opencv,map_name=None):
        
        check_img = im_opencv[1:21,606:717]
        image = self.imgPreprocessing(check_img)
        if  image is None:
            return False
         #修改通道数
        # check_img = cv2.cvtColor(check_img, cv2.COLOR_BGR2RGB)
        # image = np.array(check_img)

        txt  = ocrUtil.detectImgOcrText(image,0)
        
        if not GAMEINFO.gameState:
            GAMEINFO.currentMap=None
            return False

        # for txt in txts:
        #     print('txt:',txt)
        if txt is not None:
            if '频道' in str(txt):
                logger.warning('在城镇中')
                GAMEINFO.currentMap=None
                GAMEINFO.gameState = False
                return False
            else:
                logger.debug('识别的地图名称为:{}',txt)
                if map_name is None:
                    GAMEINFO.currentMap=txt
                    return True
                else:
                    if txt == map_name:
                        logger.debug('识别到地图名称为:{}',txt)
                        GAMEINFO.currentMap=txt
                        return True    
        return False

    '''
        获取并移动到推荐地图
        参数: sel_map_str 需要选中的推荐地图序号

    '''
    def gotoRecommendMap(self,sel_map_str):
        sel_map_index = int(sel_map_str)
        winApi.keyRelease()

        winApi.showWindow()
        time.sleep(0.5)
        ocrRes = None
        ocrText = None
        ocrLeftUp = [354,140]
         # todo 死循环
        while ocrText != '成长/装备指南':
            winApi.keyDown('ES')
            time.sleep(0.5)
            full_img = winApi.getGameImg()
            step_img = full_img[140:170,354:470]
            image = self.imgPreprocessing(step_img)
            # cv2.imshow('step_img',image)
            # cv2.waitKey(0)

            try:
                ocrRes = ocrUtil.detectImgOcr(image)
                ocrText = [detection[1][0] for line in ocrRes for detection in line][0] if len(ocrRes) > 0 else None
            except Exception as e:
                logger.error('识别失败:{}',e)
                cv2.imwrite('test/img/detect_error.jpg',image)
            
        boxes = [detection[0] for line in ocrRes for detection in line]
        # print('boxes:',boxes)
        # 找出矩形的左上角点（x1, y1）和右下角点（x2, y2）
        box = boxes[0]
        (x1, y1) = (min(point[0] for point in box), min(point[1] for point in box))
        (x2, y2) = (max(point[0] for point in box), max(point[1] for point in box))
        # 计算中心点坐标
        center_x = ocrLeftUp[0] + int((x1 + x2) / 2)
        center_y = ocrLeftUp[1] + int((y1 + y2) / 2)

        time.sleep(0.5)
        # print("窗口左上角坐标:",app_head)
        print(f'step1移动到绝对位置{GAMEINFO.gameRect["x"]+center_x},{GAMEINFO.gameRect["y"]+center_y}')
        winApi.moveAbsClick(GAMEINFO.gameRect['x']+center_x,GAMEINFO.gameRect['y']+center_y)
        time.sleep(0.2)
        
        # 移动到普通地下城
        winApi.moveAbsClick(GAMEINFO.gameRect['x']+234,GAMEINFO.gameRect['y']+103)
        time.sleep(0.2)
        
        full_img = winApi.getGameImg()
        # map_img = full_img[180:274,37:763]
        mid_map_img = full_img[188:267,314:490]
        cur_index = 0
        # 获取推荐地图海伯伦
        logger.info('获取推荐地图信息')
        while cur_index != sel_map_index:  
            # 
            full_img = winApi.getGameImg()
            # map_img = full_img[180:274,37:763]
            mid_map_img = full_img[188:267,314:490]        
            mid_text_img_dir = r'startUI/img/map_list/'

            for i in range(1, 15):
                padded_i = f'{i:02d}' if i < 10 else str(i)
                mid_text_imgpath = mid_text_img_dir + f'{padded_i}.jpg'
                mid_text_img = cv_imread(mid_text_imgpath)
                
                # print('padded_i:',mid_text_img_dir + f'{padded_i}.jpg')
                isMid,coordinate = find_one_picd(mid_map_img, mid_text_img, 0.8)

                if isMid:
                    cur_index = i
                    # cv2.imshow('mid_text_img',mid_text_img)
                    # cv2.waitKey(0)
                    print(f'当前推荐地图选中{cur_index}图左上角坐标:{coordinate[0]},{coordinate[1]}')
                    if i == sel_map_index:
                        logger.info(f'找到推荐地图{padded_i}.jpg,选择瞬移过去')
                        winApi.moveAbsClick(GAMEINFO.gameRect['x']+314+int(coordinate[0]),GAMEINFO.gameRect['y']+188+int(coordinate[1]))
                        time.sleep(1)
                        winApi.keyDown('ES')
                        return sel_map_index
                    elif i < sel_map_index:
                        wheel_num = sel_map_index-i
                        print(f'未找到地图,向右滚动{wheel_num}轮寻找')
                        self.mouse.send_data_absolute(GAMEINFO.gameRect['x']+314+int(coordinate[-2]),GAMEINFO.gameRect['y']+188+int(coordinate[-1]))
                        
                        for i in range(wheel_num):
                            self.mouse.send_wheel_data(-2)
                            time.sleep(0.02)
                    elif i > sel_map_index:
                        wheel_num = i-sel_map_index
                        print(f'未找到地图,向左滚动{wheel_num}轮尝试')
                        self.mouse.send_data_absolute(GAMEINFO.gameRect['x']+314+int(coordinate[-2]),GAMEINFO.gameRect['y']+188+int(coordinate[-1]))
                        for i in range(wheel_num):
                            self.mouse.send_wheel_data(2)
                            time.sleep(0.02)
            
                    break
            time.sleep(0.2)    

        return None

    """
        走到普通地图
        参数: 
            - direction 进入选择地图界面需要输入的方向
            - tar_map_str 需要进入的地图名称 

    """
    def goIntoMap(self,direction,tar_map_str):
        # 人物向右进图
        if direction == 'right':
            self.keyboard.send_data('66')
        elif direction == 'left':
            self.keyboard.send_data('44')
        time.sleep(3)
        self.keyboard.release()

        tryCount = 0
        while tryCount <= 10:
            full_img = winApi.getGameImg()
            cur_img = full_img[288:391,0:230]
            image = self.imgPreprocessing(cur_img)
            txts  = ocrUtil.detectImgOcrText(image)
            logger.debug('txts:',txts)
            
            # for txt in txts:
            #     print('txt:',txt)
            if len(txts)>0 and txts[0] == tar_map_str:
                logger.info('找到目标地图，准备进入')
                break
            else:
                logger.info('尝试寻找地图。。')
                winApi.keyDown('22')
                # 随机等待0.2-0.3s执行
                winApi.randomDelay(0.2,0.3)
                tryCount += 1

        if tryCount > 10:
            logger.warning('未找到目标地图，退出')
            return False
        
        # 连续按4次右键，确保最高难度
        for i in range(4):
            winApi.keyDown('66')
            # 随机等待0.2-0.4s执行
            winApi.randomDelay(0.2,0.4)
        
        return True


if __name__ == '__main__':
    GAMEINFO.queryJobList()                                                      
    roleInfo = RoleInfo()
    roleInfo.dismantlingEquipment()
    # roleInfo.changeRole()
