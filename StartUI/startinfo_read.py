from paddleocr import PaddleOCR, draw_ocr

def detectImg():
    # 模型路径下必须含有model和params文件
    ocr = PaddleOCR(det_model_dir='ocr/model/det', rec_model_dir='ocr/model/rec', rec_char_dict_path=None, cls_model_dir='ocr/model/cls', use_angle_cls=True)
    img_path = 'test/img/角色选择.jpg'
    result = ocr.ocr(img_path, cls=True)
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

    im_show = draw_ocr(image, boxes, txts, scores, font_path='ocr/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('result.jpg')

    return result


    

if __name__ == '__main__':
    detectImg()
