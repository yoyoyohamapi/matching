# coding: utf8
import cv2
import numpy as np

def extractSkinColor(image):
    """
    分割

    Args:
        image 源图像
    Return:
        dst 目标图像
    """
    # 正脸的级联分类器
    faceCascade = cv2.CascadeClassifier("./cascades/haarcascade_frontalface_default.xml")
    # 转换成灰度图才能进行面部检测
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) == 0:
        return None
    else:
        face = faces[0]
        # TODO：提取面部中的主要颜色
        # TODO：计算与预定义的肤色的距离，获得肤色

def preProcess(image):
    """
    预处理

    Args:
        image 源图像
    Return:
        dst 目标图像
    """

def extractColor(image):
    """
    Args:
        image 源图像
    Return:
        color 颜色
    """
    # TODO: 判断是单色图还是彩色图


if __name__ == "__main__":
    # 读取图像
    image = imread('face.jpg')
    if image is None:
        return
    # 预处理后的图像
    preProcessedImg = preProcesse(image)
    # 分割
    cutImg = extractSkinColor(preProcessedImg)

    # 颜色提取
    a
