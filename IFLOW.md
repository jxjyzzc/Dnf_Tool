# IFLOW - DNF自动化工具

## 项目概述

IFLOW是一个基于Python开发的DNF（地下城与勇士）游戏自动化工具集，通过计算机视觉和人工智能技术实现智能刷图功能。系统集成了目标识别、路径规划、技能释放和硬件控制等多个核心模块。

### 核心特性

- **多地图支持**: 支持白云塔、风包妖城、海伯伦等多个经典地图
- **智能识别**: 基于YOLO深度学习模型的目标检测系统
- **自动化控制**: 全自动移动、战斗、拾取物品和技能释放
- **硬件兼容**: 支持CH9329键盘鼠标模拟器硬件设备
- **模块化设计**: 采用模块化架构，易于扩展和维护

## 技术架构

### 核心技术栈

- **开发语言**: Python 3.x
- **计算机视觉**: OpenCV 4.6.0、OpenCV-Contrib
- **深度学习**: YOLO目标检测、TensorFlow、ONNX推理引擎
- **OCR识别**: PaddleOCR文字识别
- **硬件控制**: PyAutoGUI、pywin32、pyserial
- **图像处理**: Pillow、matplotlib、numpy
- **日志系统**: Loguru

### 项目结构

```
Dnf_Tool/
├── ch9329Comm/          # 串口通信模块
│   ├── keyboard.py      # 键盘控制
│   ├── mouse.py         # 鼠标控制
│   └── BezierTrajectory.py  # 贝塞尔轨迹
├── config/              # 配置文件
│   ├── cfg.py           # 主配置
│   ├── game_info.ini    # 游戏信息配置
│   └── key_codes.py     # 按键映射
├── controller/          # 控制器模块
│   └── gomap_controller.py  # 地图控制
├── gameUtils/           # 游戏工具类
│   ├── Entity.py        # 实体对象
│   ├── GameInfo.py      # 游戏信息管理
│   ├── LoadData.py      # 数据加载
│   ├── MiniMapTools.py  # 小地图工具
│   ├── SIFTLoc.py       # SIFT位置定位
│   ├── WindowsAPI.py    # Windows API接口
│   └── recognition/     # 识别模块
├── map/                 # 地图资源
│   ├── [bydt|fbyc|hbl]MiniMapTools.py  # 地图特定工具
│   ├── img/             # 地图图片资源
│   └── xml/             # 地图路径配置
├── skill/               # 技能配置
│   ├── LoadData.py      # 技能数据加载
│   ├── total_skill.xml  # 总技能配置
│   └── [职业名]_skill.xml  # 职业特定配置
├── StartUI/             # 启动界面
│   ├── Bag.py           # 背包管理
│   ├── roleInfo.py      # 角色信息
│   └── startInfoRead.py # 启动信息读取
├── task/                # 任务脚本
│   └── HblScript.py     # 海伯伦任务脚本
├── tool/                # 工具脚本
│   ├── astart.py        # 辅助启动
│   ├── getkeys.py       # 按键获取
│   ├── grabscreen.py    # 屏幕截图
│   └── ocrutil.py       # OCR工具
└── test/                # 测试文件
```

## 支持的地图

### 1. 白云塔 (Bydt)
- **脚本**: `BydtScript.py`
- **地图路径**: `map/img/bydt/`
- **配置**: `map/xml/BaiYunDengTa.xml`
- **特色**: 支持传统刷图流程

### 2. 风暴幽城 (Fbyc)
- **脚本**: `FbycScript.py`
- **地图路径**: `map/img/fbyc/`
- **配置**: `map/xml/FengbaoYoucheng.xml`
- **特色**: 复杂地形处理

### 3. 海伯伦 (Hbl)
- **脚本**: `task/HblScript.py`
- **地图路径**: `map/img/hbl/`
- **配置**: `map/xml/Haibolun.xml`
- **特色**: 使用HTTP API进行目标识别

## 核心功能模块

### 1. 目标识别系统
基于YOLO深度学习模型，能够识别：
- 玩家角色位置
- 怪物目标
- Boss目标
- 可拾取物品
- 商店界面
- 卡牌选择界面

### 2. 路径规划系统
- **SIFT特征匹配**: 使用SIFT算法进行精确位置定位
- **Bezier轨迹**: 支持贝塞尔曲线平滑移动
- **动态路径**: 根据实时情况调整移动路径

### 3. 技能释放系统
- **职业配置**: 支持多种职业的技能配置
- **冷却管理**: 智能技能冷却时间管理
- **释放时机**: 根据地图房间自动释放技能

### 4. 硬件控制
- **CH9329设备**: 支持串口键盘鼠标模拟
- **Windows API**: 底层系统键盘控制
- **精确控制**: 支持绝对坐标和相对移动

## 配置说明

### 串口配置
```python
# config/cfg.py
serial.ser = serial.Serial('COM4', 9600)  # CH9329设备串口
```

### 游戏配置
```python
# 游戏窗口配置
APP_TITLE = '地下城与勇士：创新世纪'
WIDTH, HEIGHT = 1920, 1080  # 屏幕分辨率

# 任务快捷键
TASK_KEY = 'f2'
```

### YOLO配置
```python
# gameUtils/GameInfo.py
self.yoloUrl = "http://127.0.0.1:5000/predict/yolov5"
```

## 安装和使用

### 环境要求
```bash
pip install -r requirements.txt
```

### 依赖库
- `airtest==1.3.2` - 自动化测试框架
- `opencv_python==4.6.0.66` - 计算机视觉
- `tensorflow_gpu==2.3.0` - 深度学习框架
- `onnxruntime==1.16.3` - ONNX推理引擎
- `paddleocr==2.7.0.2` - OCR文字识别
- `ch9329Comm` - 自定义串口通信库

### 使用方法

1. **启动游戏**: 首先启动DNF游戏并进入相应地图
2. **选择脚本**: 根据地图选择对应的脚本文件
3. **配置参数**: 在`config/game_info.ini`中配置相关信息
4. **运行脚本**: 执行对应的脚本文件

```bash
# 白云塔
python BydtScript.py

# 风包妖城
python FbycScript.py

# 海伯伦
python task/HblScript.py
```

## 职业技能配置

### 技能配置文件结构
```xml
<!-- skill/total_skill.xml -->
<skills>
    <skill name="阿修罗">
        <key>技能按键</key>
        <cooldown>冷却时间</cooldown>
        <cost>释放时间</cost>
    </skill>
</skills>
```

### 房间技能配置
每个地图房间可以配置不同的技能释放组合：
```python
room_skill[x][y] = [
    [入场技能列表],
    [战斗技能列表]
]
```

## 开发和调试

### 测试环境
```bash
# 图像测试
python test/imgTest.py

# 鼠标测试
python test/mouseTest.py
```

### VS Code配置
项目包含`.vscode/launch.json`配置，支持直接调试当前文件。

### 日志系统
使用Loguru进行日志记录，支持不同级别的日志输出。

## 注意事项

1. **硬件要求**: 需要CH9329硬件设备支持
2. **分辨率**: 当前配置为1920x1080分辨率
3. **网络环境**: 海伯伦地图需要YOLO服务器支持
4. **权限要求**: 需要管理员权限运行以访问系统API

## 常见问题

### 1. 串口连接失败
- 检查CH9329设备是否正确连接到COM4端口
- 确认设备驱动安装正常

### 2. 目标识别失败
- 检查YOLO服务器是否正常启动
- 确认游戏窗口在前台显示
- 调整识别阈值参数

### 3. 移动路径错误
- 检查地图配置文件是否完整
- 确认SIFT特征图片资源存在

## 版本信息

- **当前版本**: 1.2
- **支持地图**: 白云塔、风包妖城、海伯伦
- **支持的职业**: 阿修罗、女气功、召唤师等
- **最后更新**: 2025年11月17日

## 联系方式

项目由肥鹅开发，用于学习和研究目的。请在使用时遵守游戏相关法律法规。

---

*本文档详细介绍了IFLOW DNF自动化工具的各项功能和使用方法。如有疑问，请查看相关代码注释或联系开发团队。*