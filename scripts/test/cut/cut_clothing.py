# coding: utf-8
import cv2
import numpy as np
import os
import re

debugs = []

def getMask(image, filename):
    """
    获得绑定区域

    Args:
        image: 源图像
    Return:
        rect: 最大区域的外接矩形
    """
    image =  cv2.GaussianBlur(image,(3,3),0)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    rows, cols = gray.shape

    # 正脸的级联分类器
    faceCascade = cv2.CascadeClassifier(
        "../../cascades/haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(gray.copy(), 1.1, 20)
    if len(faces) > 0:
        face = faces[0]
    else:
        face = None

    # 边缘检测
    edges = cv2.Canny(gray, 100, 200, apertureSize=5)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # 获得最大轮廓
    contours, hierachy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    maxContour = contours[0]
    for contour in contours:
        if(len(contour) > len(maxContour)):
            maxContour = contour
    finalMask = None
    if face is None:
        cv2.drawContours(edges, [maxContour], 0, (255, 255, 255), cv2.FILLED)
        _,finalMask = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY)
    else:
        cv2.drawContours(edges, [maxContour], 0, (255, 255, 255), 3)
        # 一定程度的形态学腐蚀操作
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        edges = cv2.erode(edges, kernel)
        # 降噪
        edges = cv2.medianBlur(edges, 5)
        # 获得最小外接矩形
        boundingRect = cv2.boundingRect(maxContour)
        # 多边形拟合
        drawing = np.zeros((rows,cols), np.uint8)
        epsilon = 0.01 * cv2.arcLength(maxContour, True)
        approx = cv2.approxPolyDP(maxContour, epsilon, True)
        hull = cv2.convexHull(maxContour)
        cv2.drawContours(drawing, [hull], 0, (255, 255, 255), cv2.FILLED)
        cv2.drawContours(drawing, [approx], 0, (0, 0, 255), cv2.FILLED)

        # 获得凸包及多边形拟合后的轮廓
        contours, hierachy = cv2.findContours(
            drawing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

        # 获得最深的外接矩形，以便排除裤装的影响
        deepestRect = boundingRect
        for contour in contours:
            rect = cv2.boundingRect(contour)
            if rect[3] > 5:
                x,y,w,h = rect
                if y > deepestRect[1]:
                    deepestRect = rect

        # 最终用于grabcut的矩形将是 排除了人脸及裤装的
        x, y, w, h = boundingRect
        y = face[1] + face[3]
        h = h - deepestRect[3] - face[3] -face[1]
        result = image.copy()
        cv2.rectangle(result, (deepestRect[0],deepestRect[1]), (deepestRect[0] + deepestRect[2],deepestRect[1] + deepestRect[3]), (0,255,0), 2)
        cv2.rectangle(result, (face[0],face[1]), (face[0]+face[2],face[1]+face[3]), (255,0,0), 2)
        cv2.rectangle(result, (x,y), (x+w,y+h), (255,0,0), 2)
        if filename in debugs:
            cv2.imshow("rect", result)
            cv2.waitKey(0)
        mask = np.zeros((rows, cols), np.uint8)
        cv2.grabCut(image, mask, (x,y,w,h), None,
                    None, 5, cv2.GC_INIT_WITH_RECT)
        # 将背景颜色设置为0
        mask = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        finalMask = mask * 255
    # 后置操作，填充衣物边缘的沟壑，使得衣物边缘更加平滑
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    finalMask = cv2.morphologyEx(finalMask, cv2.MORPH_CLOSE, kernel, iterations=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    finalMask = cv2.morphologyEx(finalMask, cv2.MORPH_OPEN, kernel, iterations=2)

    contours, hierachy = cv2.findContours(
        finalMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    maxContour = contours[0]
    for contour in contours:
        if(len(contour) > len(maxContour)):
            maxContour = contour
    cv2.drawContours(finalMask, [maxContour], 0, (255, 255, 255), cv2.FILLED)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    finalMask = cv2.erode(finalMask, kernel)
    return finalMask

if __name__ == "__main__":
    # 批处理
    rootDir = "clothings"
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
