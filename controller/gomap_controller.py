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


def checkInMap(roleInfo,map_str=None):
    GAMEINFO.gameState = True
    im_opencv = winApi.getGameImg()
    inMap = roleInfo.isInRecommendMap(im_opencv)  
    return inMap  

def afterAutoBeatMonster(roleInfo,jobList):
    logger.info('===============刷图后续处理==================')
    roleInfo.dismantlingEquipment()
    # 分解后当前角色完成，角色列表更新
    if jobList is not None:
        GAMEINFO.modifyJobList(jobList)
    # timer.cancel()    

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
    jobList = GAMEINFO.queryJobList()
    job_postion_list = startInfoRead.startGameInfo(im_opencv)
    if len(jobList) == 0 and job_postion_list:
        logger.info('当前在角色选择界面.')
        jobList = [job[-1] for job in job_postion_list]
    GAMEINFO.modifyJobList(jobList)
    roleResult = roleInfo.getBasicRoleInfo()
    logger.debug('jobList:{},roleResult:{}',jobList,roleResult)
    print('===============开始循环脚本==================')
    GAMEINFO.gameLoop = True
    while GAMEINFO.gameLoop:
        logger.info('roleResult:{}',roleResult)
        if len(roleResult['level'])==0:
            logger.info('===============未找到图内特征,开始选择角色=================')
            curRole,nextRole = roleInfo.changeRole()
            time.sleep(3)
            roleResult = roleInfo.getBasicRoleInfo()
            time.sleep(1)
            continue
        if roleResult['power'] == '0/156':
            
            curRole,nextRole = roleInfo.changeRole()
            # logger.debug('pre modify jobList:{}',jobList)
            if curRole in jobList:
                logger.info('{} 疲劳为0,角色列表中移除该角色',curRole)
                jobList.remove(curRole)
                GAMEINFO.modifyJobList(jobList)
                
            jobList = GAMEINFO.queryJobList()
            logger.debug('重新加载还剩角色列表:{}',jobList)
            if len(jobList) == 0:
                logger.info('角色列表为空，退出循环')
                GAMEINFO.gameLoop = False
                break
            time.sleep(3)
            roleResult = roleInfo.getBasicRoleInfo()
            time.sleep(1)
            continue
        if roleInfo.gotoRecommendMap('06')==6:
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
                        afterAutoBeatMonster(roleInfo,jobList)
                        continue
                else:
                    logger.warning('进入普通地图失败')
        time.sleep(0.5)