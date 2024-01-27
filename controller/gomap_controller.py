import sys,os
# 获取项目根目录
root_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.join(root_dir, "..")
sys.path.append(project_dir)

from startUI.RoleInfo import RoleInfo
import startUI.startInfoRead as startInfoRead
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

def indexConfigROI(left,top,right,bottom,postionList):
    rect =  Rectangle(left,top,right,bottom)  
    logger.debug('left,top,right,bottom:{}',(left,top,right,bottom))
    logger.debug('postionList:{}',postionList)
    
    for i in range(len(postionList)):
        postion = ast.literal_eval(str(postionList[i]))
        
        logger.debug('postion:{}',*postion)
        if rect.is_center_near(Rectangle(*postion),5):
            logger.info('当前区域在配置文件区域目标：{}',postion)
            return i
    return -1    


def markOrRemovezeroPower(postionList,removeIndex):
    powerList = GAMEINFO.powerlist
    if int(removeIndex)>-1:
        # postionList.remove(removePostion)
        if powerList is None or len(powerList)==0:
            return None,None
        powerList[removeIndex] = 0
        GAMEINFO.saveCurRoleIndex(removeIndex)
        logger.debug('目标power{}标记为0....',removeIndex)
    
     # 如果powerList所有元素都为0，则移除postionList及powerList所有元素    
    if len(powerList)>0 and all([power == 0 for power in powerList]):
            postionList = []
            powerList = []
            GAMEINFO.gameLoop = False
            GAMEINFO.saveCurRoleIndex(-1)
            GAMEINFO.modifyRolePosition([],[])
            return []

    GAMEINFO.modifyRolePosition(postionList,powerList)
        
    postionList,powerList = GAMEINFO.queryJobList()
    logger.debug('重新加载还剩角色列表:{}',postionList,',powerList:{}',powerList)
    return postionList

def afterAutoBeatMonster(roleInfo,postionList):
    logger.info('===============刷图后续处理==================')
    roleInfo.dismantlingEquipment()
    curPostion,nextPostion = roleInfo.changeRole()    
    removeIndex = indexConfigROI(*curPostion,postionList)
   
    logger.info('index {} 疲劳为0,角色列表中移除该角色',removeIndex)
    postionList = markOrRemovezeroPower(postionList,removeIndex)
    return postionList
    

def initPostionConfig(postionList,powerList): 
    # 当前未选定角色，可以初始化
    if int(GAMEINFO.getCurRoleIndex()) == -1:   
        im_opencv = winApi.getGameImg()
        inStartGame = startInfoRead.isInStart(im_opencv)
        if not inStartGame:
            logger.warning('不在角色选择界面，无法初始化postionList')
            return False
        job_postion_list = startInfoRead.startGameInfo(im_opencv)
        
        if len(job_postion_list) > 0:
            postionList = [job[0] for job in job_postion_list]
        else:
            postionList = []
            GAMEINFO.saveCurRoleIndex(-1)

        powerList = ['156']*len(postionList)

        logger.info('初始化postionList成功,postionList:{}',job_postion_list)
        GAMEINFO.modifyRolePosition(postionList,powerList)
        return True
    else:
        logger.warning('初始化postionList失败,game_info.int中 cur_index 不为-1')
        return False

if __name__=="__main__":
    roleInfo = RoleInfo()
    postionList,powerList = GAMEINFO.queryJobList()
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
       isFinish =  hbl.autoBeatMonster('阿修罗')
       # 出图分解装备
       if isFinish:
           time.sleep(2)
           afterAutoBeatMonster(roleInfo,postionList)
 
    print('===============开始获取当前人物可刷图信息==================')
    
    GAMEINFO.gameLoop = True
    if len(postionList)==0:
        logger.info('===============配置信息未加载角色信息，进行可刷图角色寻找================') 
        inStartGame = initPostionConfig(postionList,powerList)
        while GAMEINFO.gameLoop:
            if not inStartGame:
                roleInfo.changeRole()
                inStartGame = initPostionConfig(postionList,powerList)
                time.sleep(2)
            else:
                break    

    postionList,powerList = GAMEINFO.queryJobList()
    if postionList is None and len(postionList):
        logger.warning('postionList为空,初始化角色失败')
        exit()

    logger.debug('postion_list:{}',postionList)
    print('===============开始循环脚本==================')
    roleResult = roleInfo.getBasicRoleInfo()
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
            removeIndex = indexConfigROI(*curPostion,postionList)
            logger.info('{} 疲劳为0,角色列表中移除该角色',removeIndex)
            postionList = markOrRemovezeroPower(postionList,removeIndex)

            if len(postionList) == 0:
                logger.info('===============可刷图角色列表为空,刷图结束==================')
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
                    isFinish =  hbl.autoBeatMonster('阿修罗')
                    # 出图分解装备
                    if isFinish:
                        time.sleep(2)
                        postionList = afterAutoBeatMonster(roleInfo,postionList)
                        
                        if len(postionList) > 0:
                            roleResult = roleInfo.getBasicRoleInfo()
                            continue
                        else:
                            logger.info('===============可刷图角色列表为空,刷图结束==================')
                            break    
                else:
                    logger.warning('进入普通地图失败')
        time.sleep(0.5)