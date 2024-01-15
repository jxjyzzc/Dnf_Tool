
import numpy
import time
import cv2
from PIL import Image
import logging
from loguru import logger

#sys.path.append('path/项目包名directory')（添加模块完整路径）参考第二种方法
# test目录引用其它类的包需要sys.path.append('.')
#注意或者sys.path.append('.')或者直接引入包名
# import sys
# sys.path.append(".") 

from yolo.yolo import YOLO,YOLO_ONNX

from map.HblMiniMapTools import miniMapTools
from gameUtils.SIFTLoc import siftLoc
from gameUtils.LoadData import loadRoomExport
from gameUtils.GameInfo import GAMEINFO
from gameUtils.Entity import Entity
import os,sys,time
import random,math

from gameUtils.WindowsAPI import winApi
from skill.LoadData import loadJob

# keyboard.send_data('HHEELLLLOO')  # 按下HELLO
# keyboard.release()  # 松开

# mdc = mouse.DataComm()
# mdc.send_data_absolute(500,500)


#实例化yolo
yolo = YOLO()
# 获取游戏窗口
winApi.getHwnd()
# 键盘操作接口
keyboard = winApi.getKeyboard()

# cv2.namedWindow('im_opencv')  # 命名窗口

roomExport = loadRoomExport(r"map\xml\Haibolun.xml")

def moveTime(dest,zero):

    speedx = GAMEINFO.speedX
    speedy = GAMEINFO.speedY
    # print('moveTime:',dest,zero)
    x_distance = int(dest[0]) - int(zero[0])
    y_distance = int(dest[1]) - int(zero[1])

    x_time = abs(x_distance / speedx)
    y_time = abs(y_distance / speedy)

    return x_time,y_time

def distanceTo(p1,p2):

    return math.sqrt(pow(p1.x - p2.x,2)  + pow(p1.y - p2.y,2))

# total_skill,room_skill = loadJob('女气功')
total_skill,room_skill = loadJob('阿修罗','hbl')
print("---------------------------")
print("当前职业所有技能：",total_skill)
print("房间释放技能组合：",room_skill)
# 初始化记录技能释放时间使用
nowTimeMap = {}
for k in total_skill:
    sk = k[0]
    nowTimeMap[sk]= 0
print('初始化技能记录状态:',nowTimeMap)    
print("---------------------------")


## s释放技能，如果当前地图技能释放完毕则进行平a
def mapSkill(t_skill,skill):
    if skill != None:

        for v in skill: 
            for k in t_skill:
                # todo 需要确保按键准确对应键盘的ch9329编码,不然会按到一个键位死循环
                if k[0] == v:
                    # 释放该技能时间
                    pressTime = nowTimeMap[v]
                    costTime = float(k[3])
                    cd = float(k[1])
                    if pressTime is not None and pressTime != 0:
                        t = int(time.time())
                        # 当前时间已超过上次释放该技能时间，恢复释放技能计时
                        if t > int(pressTime + cd + costTime):
                            nowTimeMap[v]=0
    
                    if nowTimeMap[v] is None or nowTimeMap[v] == 0:
                        nowTimeMap[v]= int(time.time())
                        
                        return (v,costTime)
                   
    return ("X",0)




# 自动打怪
def autoBeatMonster():
    playerSpeed= {'x':0,'y':0,'b':0}




    preRoomId = None        #上一个房间ID

    tryCount = 0
    maxCount = 5

    SELECT = False
    SERVICE = False
    OVERFLOW = False
    CHALLENGE_AGAIN = False
    SET_ITEM = False

    try:
        while True:
            SELECT = False
            SHOP = False
            # 进入后看不到boss的房间用到该变量
            bossMove = False

            # 获取游戏图像
            im_opencv = winApi.getGameImg()
            # 获取小地图图像
            miniMap = miniMapTools.getMimiMapImg(im_opencv)
            # print('miniMap shape:',miniMap.shape)
            # 获取房间id
            room_id = miniMapTools.getPlayerRoomId()
            boss_roomid = miniMapTools.getBossRoomId()
            liefeng_roomid = miniMapTools.getLiefengRoomId()


            # 进入boss房间情况
            if room_id is None:
                if liefeng_roomid is not None:
                    # 还没写相关逻辑
                    print('发现裂缝地图%s,需要处理进入boss图'%liefeng_roomid)
                    room_id = liefeng_roomid
                    # 裂缝出现则不认为目前在boss房间
                elif boss_roomid is not None:
                    print('当前进入boss房间：',boss_roomid)
                    room_id = boss_roomid
                

            #修改通道数
            im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2RGB)

            #转换数据类型
            im_PIL = Image.fromarray(
                im_opencv
            )
            # 识别的图像
            r_image, labels = yolo.detect_image(im_PIL)
            

            hero = Entity()
            boss = Entity()
            monsters = []
            articles = []
            card_size = 0
            for _ in labels:
                label = _['label'].decode('utf-8')
                top = int(_['top'])
                left = int(_['left'])
                bottom = int(_['bottom'])
                right = int(_['right'])
                label = label.split(" ")[0]
                # print('label,top,left,bottom,right:',label,top,left,bottom,right)

                if label == "hero":

                    x_center = left + (right - left) / 2
                    # 由于标记的样本把人名也框选，所以与课程有区别用bottom做参照
                    y_center = bottom + GAMEINFO.playerHeight
                    hero.setPosition(x_center,y_center,right - left,GAMEINFO.playerHeight,"hero")   

                
                if label == "boss":
                    x_center = left + (right - left) / 2
                    y_center = bottom
                    boss.setPosition(x_center,y_center,right - left,y_center,"boss")
                    bossMove = True
                    # 进boss房 liefeng_roomid会影响操作
                    liefeng_roomid = None    
                if label == "monster":
                    m = Entity()
                    x_center =  left + (right - left)/2
                    y_center =  top + (bottom - top)
                    m.setPosition(x_center,y_center,right - left,bottom - top,"monster")
                    monsters.append(m)    

                if label == "article":
                    m = Entity()
                    x_center =  left + (right - left)/2
                    y_center =  top + bottom - top
                    m.setPosition(x_center,y_center,right - left,bottom - top,"article")
                    articles.append(m)   

                if label =="select":
                    SELECT = True

                if label == "shop":
                    SHOP = True

                if label == "service":
                    SERVICE = True

                if label == "overflow":
                    OVERFLOW = True     
                if label == "card":
                    card_size = card_size+1


            if card_size == 4:
                print('跳过卡牌选择界面')
                keyboard.send_data("ES")
                keyboard.release()
                # 翻盘时间慢这里等待长点
                time.sleep(2.5)

            if SELECT == True:
                
                if SHOP == True:
                    print('刷图完毕，判断是否需要修理出售物品')
                    if OVERFLOW == True:
                        time.sleep(2)
                        keyboard.send_data("AA")
                        time.sleep(1)
                        keyboard.send_data("SP")
                        time.sleep(1)
                        keyboard.send_data("44")
                        time.sleep(1)
                        keyboard.send_data("SP")
                        time.sleep(1)
                        OVERFLOW = False


                    if SERVICE == True:
                        time.sleep(2)
                        keyboard.send_data("SS")
                        time.sleep(2)
                        keyboard.send_data("SP")
                        time.sleep(2)
                        SERVICE = False
                        
                
                    # 关闭商店才能操作捡取物品
                    print('关闭商店进行后续操作...')
                    keyboard.send_data("ES")
                    keyboard.release()
                    time.sleep(0.5)
                    continue
                else:
                    # 如果当前boss图没有物品
                    if len(articles) == 0 and CHALLENGE_AGAIN is True:
                        print('------------------再次挑战---------------------')
                        keyboard.send_data("N6")
                        keyboard.release()
                        # 一般要延迟一会才会重新挑战
                        time.sleep(5)
                        # 重置技能释放时间记录
                        for k in total_skill:
                            sk = k[0]
                            nowTimeMap[sk]= 0
                        continue
                    else:
                        if SET_ITEM is False:
                            print('----------------一键聚物--------------------')
                            keyboard.send_data("N0")
                            keyboard.release()
                            SET_ITEM = True

                    
                        if SET_ITEM is True:
                            print('捡取物品．')
                            keyboard.send_data("XX")
                            time.sleep(2)
                            keyboard.release()
                            print('当前状态可以进行再次挑战。。。。')
                            CHALLENGE_AGAIN = True
                            continue
            else:
            # print('重置一键聚物状态................')
                SET_ITEM = False
                # print('重置重新挑战状态................')
                CHALLENGE_AGAIN = False


            # 黑屏时继续循环
            if room_id is None and boss_roomid is None and SELECT is False:
                # print('房间id获取失败')
                continue  

            #新房间
            if preRoomId != room_id:

                print('roomId:',room_id)
                # print('total_skill:',total_skill)
                # print('---------------')
                print('room_skill:',room_skill)
                x,y = room_id.split("_")
                x = int(x)
                y = int(y)

                k = room_skill[x][y]
                # print('当前房间应放技能:',k)
                if k != None and len(k)>1:
                    if k[0] != None:
                        state_skill = k[0]
                    if k[1] != None:
                        current_room_skill = k[1]

                if len(state_skill) >0:
                    for i in range(len(state_skill)):
                        k = state_skill[i]
                        if not k is None:  
                            if len(k) == 1:
                                k = k + k
                            # ch9329模块按键字符要重复2次同一个字符来输出    
                            keyboard.send_data(k)
                            keyboard.release()
                            # 等待技能释放完毕
                            time.sleep(1)
                    state_skill = []

                #  boss门口见不到怪则向右跑1s寻找
                if bossMove == False and room_id == boss_roomid:
                    keyboard.send_data("66")
                    keyboard.release()
                    keyboard.send_data("66")
                    time.sleep(1)
                    keyboard.release()    

                preRoomId = room_id        

            if playerSpeed['b'] == 0:
                print('测试人物跑动移速...')
                room_image_path = f"map/img/hbl/hbl_{room_id}.jpg"
                if os.path.exists(room_image_path):
                # 人物在整个房间中的位置
                    x,y = siftLoc.getSiftLoc(room_image_path,im_opencv)
                    print('当前位置与大地图偏移量：%s,%s'%(x,y))

                # 重试3次失败再停止程序
                if x is None or y is None:
                    if tryCount>maxCount:
                        print('重试3次失败，程序退出')
                        break
                    else:
                        tryCount = tryCount + 1
                        print('重试第%s次'%tryCount)
                        continue

                # player_x,player_y 大地图测移速用
                player_x = x + hero.x
                player_y = y + hero.y
                print("测速大地图[%s],人物坐标：（%s,%s)" % (room_id, player_x, player_y))

                
                if playerSpeed['x'] == 0  or playerSpeed['y'] == 0:
                    playerSpeed['x'] = player_x
                    playerSpeed['y'] = player_y
                    
                    print('playerSpeed[%s](%s)记录成功,开始跑动测速'%(playerSpeed['b'],playerSpeed))
                    # 跑0.5s钟计算位移坐标 (因为跑的时间过长可能会达到版边)
                    keyboard.send_data('66')  # 按下HELLO
                    keyboard.release()  # 松开
                    keyboard.send_data('66')  # 按下HELLO
                    time.sleep(0.5)
                    keyboard.release()  # 松开

                    # 向上移动
                    keyboard.send_data('88')  # 按下HELLO
                    time.sleep(0.5)
                    keyboard.release()  # 松开
                    continue

                else:
                    print('计算速度')
                    speedx = abs(player_x - playerSpeed['x']) * 2
                    speedy = abs(player_y - playerSpeed['y']) * 2
                # 各种问题造成测试速度过低，则重新测试速度
                    if int(speedx) < 20 or int(speedy) < 20 or int(speedx)>1000 or int(speedy) > 500:
                        print('计算速度不在正常区间，重新计算...')
                        playerSpeed['x'] = 0
                        playerSpeed['y'] = 0
                        continue
                    #大致数值 473.2932035462136 179.85576946159154
                    print("计算出人物移动速度：",speedx,speedy)
                    playerSpeed['b'] = 1
                    GAMEINFO.speedX = speedx
                    GAMEINFO.speedY = speedy
                    continue
            # exit()        
                
                    
            if boss.name == "boss":
                print('发现boss （%s,%s）， 人物 (%s,%s)  ...' % (boss.x,boss.y,hero.x,hero.y))

                y_dist = 60
                x_dist = 200

                # 防止意外人物不走动
                if tryCount > maxCount:
                    winApi.release()
                    tryCount = 0

                if boss.y - hero.y < -y_dist:
                    keyboard.send_data("88")
                    continue

                if boss.y - hero.y > y_dist:
                    keyboard.send_data("22")
                    continue

                if boss.x - hero.x > x_dist:
                    # 当前是跑动状态，要松开键盘
                    winApi.downDouble('66')
                    tryCount = tryCount+1
                    continue

                if boss.x - hero.x < -x_dist:
                    # 当前是跑动状态，要松开键盘
                    winApi.downDouble('44')
                    tryCount = tryCount+1
                    continue
                
                # 人物与boss重合会无法识别到，hero.x可能为0
                if abs(boss.x - hero.x) <= x_dist or hero.x == 0:
                    print('开始攻击boss （%s,%s）， 人物 (%s,%s)  ...' % (boss.x,boss.y,hero.x,hero.y))
                    if hero.x!=0 and boss.x - hero.x > 0:
                        keyboard.send_data("66")
                        winApi.release()

                    if hero.x!=0 and boss.x - hero.x < 0:
                        keyboard.send_data("44")
                        winApi.release()

                k,costTime = mapSkill(total_skill,current_room_skill)
                print('当前图应按键：',k,'按住时间：',costTime)

                if k == "X":
                    for i in range(3):
                        keyboard.send_data("XX")
                        winApi.release()
                        time.sleep(0.2)
                    continue

                if len(k) == 1:
                    k = k + k

                keyboard.send_data(k)
                time.sleep(costTime)
                winApi.release()

            # 自动打怪
            if len(monsters) > 0:

                directions = []
                for monst in monsters:
                    d = distanceTo(hero,monst)
                    directions.append(
                        {
                            "direction":abs(d),
                            "monster":monst
                        }
                    )

                #将列表中值根据direction从小到大排序，找到距离人物最近的怪物
                sorted_list = sorted(directions,key=lambda x:x['direction'])
                monster = sorted_list[0]['monster']

                print('最近怪物坐标 （%s,%s）， 人物坐标 (%s,%s) ' % (monster.x,monster.y,hero.x,hero.y))
                # 进行攻击怪物的阈值
                y_dist = 30
                x_dist = 180
                
                # 防止意外人物不走动
                if tryCount > maxCount:
                    winApi.release()
                    tryCount = 0
        
                # 向怪物移动
                if monster.x - hero.x > x_dist:
                    # 当前是跑动状态，要松开键盘
                    winApi.downDouble('66')
                    tryCount = tryCount+1
                    continue

                if monster.x - hero.x < -x_dist:
                    # 当前是跑动状态，要松开键盘
                    winApi.downDouble('44')
                    tryCount = tryCount+1
                    continue

                if monster.y - hero.y < -y_dist:
                    keyboard.send_data("88")
                    continue

                if monster.y - hero.y > y_dist: 
                    keyboard.send_data("22")
                    continue

                
                # 人物移动到可攻击范围时
                if abs(monster.x - hero.x) <= x_dist:
                    print('开始攻击：怪物坐标 （%s,%s）， 人物坐标 (%s,%s) ' % (monster.x,monster.y,hero.x,hero.y))
                    
                    # 判断调整怪物与人物的朝向
                    if monster.x - hero.x > 0:
                        keyboard.send_data("66")
                        winApi.release()

                    if monster.x - hero.x < 0:
                        keyboard.send_data("44")
                        winApi.release()
            

                k,costTime = mapSkill(total_skill,current_room_skill)
                print('当前图应按键：',k,'按住时间：',costTime)

                if k == "X":
                    for i in range(3):
                        keyboard.send_data("XX")
                        winApi.release()
                        time.sleep(0.2)
                    continue

                if len(k) == 1:
                    k = k + k

                keyboard.send_data(k)
                time.sleep(costTime)
                winApi.release()  
                

            # 拾取物品
            if len(monsters) == 0 and len(articles) > 0:
                print('--------------开始捡取物品---------------')
                directions = []
                for article in articles:
                    d = distanceTo(hero,article)
                    directions.append(
                        {
                            "direction":abs(d),
                            "article":article
                        }
                    )

                #将列表中值根据direction从小到大排序，找到距离人物最近的物品
                sorted_list = sorted(directions,key=lambda x:x['direction'])
                article = sorted_list[0]['article']
                print("人物坐标：",(hero.x,hero.y))
                print('距离人物最近的物品坐标：',(article.x,article.y))
                # 进行向物品移动的时间
                x_time,y_time = moveTime([article.x,article.y],[hero.x,hero.y])

                # # 向物品移动
                if article.y - hero.y < 0:
                    keyboard.send_data("88")
                    time.sleep(y_time)
                    winApi.release()
                    
                else:
                    keyboard.send_data("22")
                    time.sleep(y_time)
                    winApi.release()
                
                if article.x - hero.x > 0:
                    keyboard.send_data("66")
                    winApi.release()
                    keyboard.send_data("66")
                    time.sleep(x_time)
                    winApi.release()
                    
                else:
                    keyboard.send_data("44")
                    winApi.release()
                    keyboard.send_data("44")
                    time.sleep(x_time)
                    winApi.release()

                tryCount = tryCount+1
                if tryCount > maxCount:
                    print('------------当前拾取失败次数过多,尝试随机走动--------')
                    # 随机移动防止卡死
                    directArr = ['44','22','66','88']
                    randomDirect = random.choice(directArr)
                    keyboard.send_data(randomDirect)  
                    time.sleep(random.random()*3)
                    tryCount = 0    

                # 人物移动到拾取范围时
                if abs(article.x - hero.x) <= 10 and abs(article.y - hero.y) <= 15:
                    time.sleep(0.5)
                    keyboard.send_data("XX")
                    winApi.release()
                    continue

            

            # # 自动过图,测速完成后再过图，不然计算速度不准刷图效果极差
            if playerSpeed['b'] == 1 and len(monsters) == 0  and len(articles) == 0:
                print('--------------开始自动过图-------------------')
                # 有时黑屏未获取roomId,重新读取图片
                im_opencv = winApi.getGameImg()
                # 获取小地图图像
                miniMap = miniMapTools.getMimiMapImg(im_opencv)
                # print('miniMap shape:',miniMap.shape)
                # 获取房间id
                new_room_id = miniMapTools.getPlayerRoomId()
                # 裂缝图看不到当前人物位置
                if new_room_id is None and liefeng_roomid is not None:
                    new_room_id = room_id = liefeng_roomid
                if new_room_id!=room_id:
                    continue
            
                # 肉眼检查下检查图片大小、颜色是否正常，按下了'esc'键退出，其它键位继续后面逻辑
                # cv2.imshow("im_opencv",im_opencv)
                # if cv2.waitKey(0) & 0xFF == 27:
                #     break

                # siftLoc检测通道数要匹配上
                im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2RGB)
                room_image_path = f"map/img/hbl/hbl_{new_room_id}.jpg"
                if os.path.exists(room_image_path):
                # 人物在整个房间中的位置
                    x,y = siftLoc.getSiftLoc(room_image_path,im_opencv)

                if x is None or y is None:
                    print("未获取到%s地图入口，重试" %new_room_id)
                    continue
                # if x > im_opencv.shape['x'] or y > im_opencv.shape['y']:
                #     print("计算小图片偏移量错误,重新计算")
                #     continue
                

                # player_x,player_y 大地图测移速用                                   
                player_x = x + hero.x
                player_y = y + hero.y
                print("大地图人物坐标：",player_x,player_y)    
                
                if player_x<0 or player_y<0 or player_x > 5000 or player_y > 5000:
                    print("识别坐标过大,重新识别")
                    continue

                export = roomExport['maps'][new_room_id]
                export_x = int(export['export_x'])
                export_y = int(export['export_y'])
            
                print("门的坐标 x:",export_x,'y:',export_y)
                x_time, y_time = moveTime( [player_x,player_y] ,[export_x ,export_y])
                print("到门的时间::::x_time, y_time:",x_time, y_time)


                # 判断门的方向，避免走错其它门
                if export['direction'] == "right" or export['direction'] == "left":

                    if player_y > export_y:
                        keyboard.send_data('88')  # 按下HELLO
                        time.sleep(y_time)
                        winApi.release()
                    else:
                        keyboard.send_data('22')  # 按下HELLO
                        time.sleep(y_time)
                        winApi.release()

                    if player_x > export_x:
                        keyboard.send_data('44')  # 按下HELLO
                        winApi.release()
                        keyboard.send_data('44')  # 按下HELLO
                        time.sleep(x_time)
                        winApi.release()
                    else:
                        keyboard.send_data('66')  # 按下HELLO
                        winApi.release()
                        keyboard.send_data('66')  # 按下HELLO
                        time.sleep(x_time)
                        winApi.release()

                else:
                    if player_x > export_x:
                        keyboard.send_data('44')  # 按下HELLO
                        winApi.release()
                        keyboard.send_data('44')  # 按下HELLO
                        time.sleep(x_time)
                        winApi.release()
                    else:
                        keyboard.send_data('66')  # 按下HELLO
                        winApi.release()
                        keyboard.send_data('66')  # 按下HELLO
                        time.sleep(x_time)
                        winApi.release()

                    if player_y > export_y:
                        keyboard.send_data('88')  # 按下HELLO
                        time.sleep(y_time)
                        winApi.release()
                    else:
                        keyboard.send_data('22')  # 按下HELLO
                        time.sleep(y_time)
                        winApi.release()
                
                tryCount = tryCount+1
                if tryCount > maxCount:
                    print('------------当前地图过图重试次数过多,尝试随机走动--------')
                    # 随机移动防止卡死
                    directArr = ['44','22','66','88']
                    randomDirect = random.choice(directArr)
                    keyboard.send_data(randomDirect)  
                    time.sleep(random.random())
                    tryCount = 0
                    
                

            # img = numpy.array(r_image)
            # img = cv2.cvtColor(img,cv2.COLOR_RGB2BGR)
            # cv2.imshow("im_opencv", img)  # 显示
            # 检查用户是否按下了'esc'键退出
            # if cv2.waitKey(500) & 0xFF == 27:
            #     break
    except Exception as e:
        logger.error('打怪运行失败,msg:{}',e) 
        logger.error('出错文件:{},出错行号:{}',e.__traceback__.tb_frame.f_globals["__file__"],e.__traceback__.tb_lineno)      

    winApi.__del__()    
    # 关闭所有窗口
    cv2.destroyAllWindows()


if __name__ == '__main__':
    autoBeatMonster()
