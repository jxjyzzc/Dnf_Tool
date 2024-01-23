import sys,os
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)

from startUI.RoleInfo import RoleInfo
import startUI.startInfoRead as startInfoRead,isInStart
from loguru import logger
# from threading import Thread
from threading import Timer
import time,random
from gameUtils.WindowsAPI import winApi
from gameUtils.GameInfo import GAMEINFO 
from gameUtils.recognition.Rectangle import Rectangle,points_to_rect

def checkInMap(roleInfo,map_str=None):
    GAMEINFO.gameState = True
    im_opencv = winApi.getGameImg()
    inMap = roleInfo.isInRecommendMap(im_opencv)  
    return inMap

import ast

def inConfigROI(left,top,right,bottom,postionList):
    rect =  Rectangle(left,top,right,bottom)  
    for i in range(len(postionList)):
        postion = ast.literal_eval(postionList[i])
        logger.debug('left,top,right,bottom:{}',(left,top,right,bottom))
        logger.debug('postion:{}',*postion)
        if rect.is_center_near(Rectangle(*postion),5):
            logger.info('当前区域在配置文件区域目标：{}',postion)
            return postionList[i]
    return None    

def afterAutoBeatMonster(roleInfo,postionList):
    logger.info('===============刷图后续处理==================')
    roleInfo.dismantlingEquipment()
    # 分解后当前角色完成，角色列表更新
    if postionList is not None:
        GAMEINFO.modifyRolePosition(postionList)
    roleInfo.changeRole()    
    # timer.cancel()    

def initPostionConfig(postionList):    
    im_opencv = winApi.getGameImg()
    job_postion_list = startInfoRead.startGameInfo(im_opencv)
    
    if len(job_postion_list) > 0:
        logger.info('在角色选择界面才可初始化postionList:{}',job_postion_list)
        postionList = [job[0] for job in job_postion_list]

    GAMEINFO.modifyRolePosition(postionList)
    pass

if __name__=="__main__":
    roleInfo = RoleInfo()
    im_opencv = winApi.getGameImg()
    print('===============判断是否在图中==================')
    recommend_str = '海伯伦的预言所'
    # timer = Timer(1,checkInMap,roleInfo)

    # 先判断是否在图中打怪
    inMap = checkInMap(roleInfo)
 
    if inMap:
       logger.info('人物目前在图中..')
    #    timer.start()
       time.sleep(2)
       import HblScript as hbl
       isFinish =  hbl.autoBeatMonster('阿修罗',roleInfo)
       # 出图分解装备
       if isFinish:
           time.sleep(2)
           afterAutoBeatMonster(roleInfo,None)

    print('===============开始获取当前人物可刷图信息==================')
    postionList = GAMEINFO.queryJobList()
    if len(postionList)==0:
        logger.info('===============配置信息未加载角色信息，进行可刷图角色寻找================') 
        im_opencv = winApi.getGameImg()
        inStartGame = isInStart(im_opencv)
        while inStartGame:
            initPostionConfig(postionList)
            im_opencv = winApi.getGameImg()
            inStartGame = isInStart(im_opencv)
            roleInfo.changeRole()
            time.sleep(2)

    roleResult = roleInfo.getBasicRoleInfo()
    logger.debug('postion_list:{},roleResult:{}',postionList,roleResult)
    print('===============开始循环脚本==================')
    GAMEINFO.gameLoop = True
    while GAMEINFO.gameLoop:
        logger.info('roleResult:{}',roleResult)
        if len(roleResult['level'])==0:
            logger.info('===============未找到图内特征,开始选择角色=================')
            curPostion,nextPostion = roleInfo.changeRole()
            time.sleep(3)
            roleResult = roleInfo.getBasicRoleInfo()
            time.sleep(1)
            continue
        if roleResult['power'] == '0/156':
            curPostion,nextPostion = roleInfo.changeRole()
            # logger.debug('pre modify jobList:{}',jobList)
            
            removePostion = inConfigROI(*curPostion,postionList)
            if removePostion is not None:
                logger.info('{} 疲劳为0,角色列表中移除该角色',removePostion)
                postionList.remove(removePostion)
                GAMEINFO.modifyRolePosition(postionList)
                
            postionList = GAMEINFO.queryJobList()
            logger.debug('重新加载还剩角色列表:{}',postionList)
            if len(postionList) == 0:
                logger.info('角色列表为空，退出循环')
                GAMEINFO.gameLoop = False
                break
            time.sleep(3)
            roleResult = roleInfo.getBasicRoleInfo()
            time.sleep(1)
            continue
        elif roleInfo.gotoRecommendMap('06')==6:
            # 黑屏等待
            time.sleep(2)
            roleResult = roleInfo.getBasicRoleInfo()
            if roleResult['map'] == '克洛诺斯岛':
                logger.info('当前地图为{},进入普通地图'.format(roleResult['map']))
                intoFlag = roleInfo.goIntoMap('right',recommend_str)
                if intoFlag:
                    logger.info('开始按空格进入地图')
                    time.sleep(random.uniform(0.2,0.3))
                    winApi.keyDown('SP')
                    
                    # 进图后开始打怪
                    inMapFlag = checkInMap(roleInfo,recommend_str)
                    time.sleep(3)
                    while not inMapFlag:
                        inMapFlag = checkInMap(roleInfo,recommend_str)
                        time.sleep(3)
                    logger.info('开始自动打怪...')

                    # timer.start()
                    import HblScript as hbl
                    isFinish =  hbl.autoBeatMonster('阿修罗',roleInfo)
                    # 出图分解装备
                    if isFinish:
                        time.sleep(2)
                        afterAutoBeatMonster(roleInfo,postionList)
                        continue
                else:
                    logger.warning('进入普通地图失败')
        time.sleep(0.5)