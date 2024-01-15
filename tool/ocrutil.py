from paddleocr import PaddleOCR, draw_ocr
import cv2
import numpy as np

class OcrUtil:

    def __init__(self):
        self.ocr = PaddleOCR(det_model_dir='ocr/model/det', rec_model_dir='ocr/model/rec', rec_char_dict_path=None, cls_model_dir='ocr/model/cls',
                        use_angle_cls=False, enable_mkldnn = True)
        pass

    '''
        图片识别为ocr文字
        img_path: 图片路径
    '''    
    def detectImgOcr(self, img_path: str):
        # 模型路径下必须含有model和params文件
       
        result = self.ocr.ocr(img_path, cls=True)
        for line in result:
            print(line)
        
        # 显示结果
        from PIL import Image
        image = Image.open(img_path).convert('RGB')
        boxes = [detection[0] for line in result for detection in line]  # Nested loop added
        txts = [detection[1][0] for line in result for detection in line]  # Nested loop added
        scores = [detection[1][1] for line in result for detection in line]  # Nested loop added


        # print('boxes:',boxes)
        # print('txts:',txts)
        # print('scores:',scores)

        # im_show = draw_ocr(image, boxes, txts, scores, font_path='ocr/simfang.ttf')
        # im_show = Image.fromarray(im_show)
        # im_show.save('result.jpg')

        return result

    #读取图像，解决imread不能读取中文路径路径的问题
    def cv_imread(self, file_path):
        #imdedcode读取的是RGB图像
        cv_img = cv2.imdecode(np.fromfile(file_path,dtype=np.uint8),-1)
        return cv_img

    #读取选定区域截图信息
    def cv_imread_roi(self, file_path:str,left: float,top: float,right: float,bottom: float):
        full_img = self.cv_imread(file_path)
        cropped = full_img[top:bottom, left:right]
        # cv2.imshow("card",cropped)
        # cv2.imshow("full_img",full_img)
        # cv2.waitKey(0)   #延时显示，0代表无限延时
        return cropped

    '''
        从截图中查找图片坐标
        @param template_path: 截图路径
        @param findimg_path: 要查找的图片路径
        @param threshold: 阈值，0-1之间，0表示完全不匹配，1表示完全匹配
        @return: 匹配成功返回True, 匹配失败返回False, 匹配坐标 前2个参数为中心点坐标,后面4个参数为 left,top,right,bottom
    
    '''
    def find_one_picd(self, template_path: object, findimg_path: str, threshold: float):
        threshold = 1-threshold
        try:
            scr = self.cv_imread(template_path)
            tp = self.cv_imread(findimg_path)
            result = cv2.matchTemplate(scr, tp, cv2.TM_SQDIFF_NORMED)
        except cv2.error:
            print('文件错误：', template_path, findimg_path,'e:',cv2.error)
            try:
                scr = self.cv_imread(template_path)
                tp = self.cv_imread(findimg_path)
                result = cv2.matchTemplate(scr, tp, cv2.TM_SQDIFF_NORMED)
            except cv2.error:
                return False, None
        # h, w = scr.shape[:2]
        h, w = tp.shape[:2]
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if min_val > threshold:
            # os.remove("im_opencv.jpg")
            return False, None
        else:
            coordinate=(min_loc[0]+w/2,min_loc[1]+h/2,min_loc[0],min_loc[1],min_loc[0]+w,min_loc[1]+h)
            print(template_path, min_val, min_loc)
            print('find_one_picd 左上角坐标值:',min_loc[0],min_loc[1])
            # os.remove("im_opencv.jpg")
            return True, coordinate

    # 多模版匹配
    def find_multiple_picd(self, img_path: str, findimg_path: str, threshold: float):
        coordinates = []
        img_rgb  = self.cv_imread(img_path)
        template = self.cv_imread(findimg_path)
        h, w = template.shape[:2]

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        # 取匹配程度大于%80的坐标
        loc = np.where(res >= threshold)

        for pt in zip(*loc[::-1]):  # *号表示可选参数
            bottom_right = (pt[0] + w, pt[1] + h)
            cv2.rectangle(img_rgb, pt, bottom_right, (0, 0, 255), 2)
        # cv2.imshow('img_rgb', img_rgb)
        # cv2.waitKey(0)
        return coordinates
    
ocrUtil = OcrUtil()    