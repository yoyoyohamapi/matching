# coding: utf-8
import cv2
import numpy as np
import re
import os

def getMask(image, filename):
    """
    获得绑定区域

    Args:
        image 源图像
        filename 文件名
    Return:
        rect 最大区域的外接矩形
    """
    # 高斯模糊
    image = cv2.GaussianBlur(image, (3, 3), 0)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rows, cols = gray.shape

    # 边缘检测
    edges = cv2.Canny(gray, 100, 200, apertureSize=3)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 获得最大轮廓
    contours, hierachy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    maxContour = contours[0]
    boundingRect = cv2.boundingRect(maxContour)
    finalMask = None
    # 如果图像没有黏着有上装
    if boundingRect[1] > 20:
        x, y, w, h = boundingRect
        mask = np.zeros((rows, cols), np.uint8)
        try:
            cv2.grabCut(image, mask, boundingRect, None,
                    None, 5, cv2.GC_INIT_WITH_RECT)
        except:
            cv2.grabCut(image, mask, (50,50,cols,rows), None,
                    None, 5, cv2.GC_INIT_WITH_RECT)
        finalMask = np.where((mask == 2) | (mask == 0), 0, 255).astype('uint8')
    else:
        # 多边形拟合
        drawing = np.zeros((rows, cols), np.uint8)
        epsilon = 0.05 * cv2.arcLength(maxContour, True)
        approx = cv2.approxPolyDP(maxContour, epsilon, True)
        hull = cv2.convexHull(maxContour)
        cv2.drawContours(drawing, [hull], 0, (255, 255, 255), cv2.FILLED)
        cv2.drawContours(drawing, [approx], 0, (0, 0, 255), cv2.FILLED)

        # 获得凸包及多边形拟合后的轮廓
        contours, hierachy = cv2.findContours(
            drawing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

        # 获得最深的外接矩形，以便排除鞋子的影响
        deepestRect = boundingRect
        for contour in contours:
            rect = cv2.boundingRect(contour)
            if rect[3] > 100:
                x, y, w, h = rect
                if y > deepestRect[1]:
                    deepestRect = rect

        x, y, w, h = deepestRect
        y = y - 50
        result = image.copy()
        cv2.rectangle(result, (x - 10, y), (x + w + 20, y + h), (255, 0, 0), 2)

        mask = np.zeros((rows, cols), np.uint8)

        cv2.grabCut(image, mask, (x, y, w, h), None,
                    None, 5, cv2.GC_INIT_WITH_RECT)
        finalMask = np.where((mask == 2) | (mask == 0), 0, 255).astype('uint8')

    # Step 4.4: 进行一定的腐蚀操作，去除背景边界
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    finalMask = cv2.erode(finalMask, kernel)
    return finalMask

if __name__ == "__main__":
    # 批处理
    rootDir = "pants"
    pattern = re.compile("^[a-zA-Z0-9]+$")
    for dp, dn, fs in os.walk(rootDir):
        for f in fs:
            # 分割图像并进行存储
            filename = f.split('.')[0]
            match = pattern.match(filename)
            if pattern.match(filename):
                srcPath = os.path.join(dp, f)
                cutPath = os.path.join(dp,"%s_cut.jpg"%filename)
                maskPath = os.path.join(dp, "%s_mask.jpg"%filename)
                image = cv2.imread(srcPath)
                mask = getMask(image, filename)
                cutImage = image * (mask[:, : ,np.newaxis]/255)
                cv2.imwrite(cutPath, cutImage)
                cv2.imwrite(maskPath, mask)
