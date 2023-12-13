import win32gui,win32api,win32con,win32ui
import numpy
import cv2

hd = win32gui.GetDesktopWindow()
print("桌面句柄",hd)

# 子窗口列表
hwndChildList = []
win32gui.EnumChildWindows(hd, lambda hwnd, param: param.append(hwnd), hwndChildList)

hWnd = 0
for hwnd in hwndChildList:
    # print(hwnd,win32gui.GetWindowText(hwnd))
    if win32gui.GetWindowText(hwnd) == "地下城与勇士：创新世纪":
        print("游戏窗口句柄：",hwnd)
        hWnd = hwnd
        break

left, top, right, bot = win32gui.GetWindowRect(hWnd)
width = right - left
height = bot - top
#获取上下文句柄
hWndDC = win32gui.GetWindowDC(hWnd)
#创建设备描述表
mfcDC = win32ui.CreateDCFromHandle(hWndDC)
#内存设备描述表
saveDC = mfcDC.CreateCompatibleDC()
# 创建位图对象
saveBitMap = win32ui.CreateBitmap()
#分配存储空间
saveBitMap.CreateCompatibleBitmap(mfcDC,width,height)
#将位图对象选入到内存设备描述表
saveDC.SelectObject(saveBitMap)
#
saveDC.BitBlt((0,0), (width,height), mfcDC, (0, 0), win32con.SRCCOPY)



#获取位图信息
signedIntsArray = saveBitMap.GetBitmapBits(True)
im_opencv = numpy.frombuffer(signedIntsArray, dtype = 'uint8')
im_opencv.shape = (height, width, 4)
cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2RGB)
cv2.imwrite("im_opencv.jpg",im_opencv,[int(cv2.IMWRITE_JPEG_QUALITY), 100]) #保存
cv2.namedWindow('im_opencv') #命名窗口
cv2.imshow("im_opencv",im_opencv) #显示
cv2.waitKey(0)
cv2.destroyAllWindows()

#内存释放
win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hWnd,hWndDC)






