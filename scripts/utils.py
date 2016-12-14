# coding: utf8
import cv2
import numpy as np


def sharpen(image, size):
    """
    锐化

    Args:
        image: 源图像
        size: 锐化窗口
    Return:
        dst: 目标图像
    """
    grayImage = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.Laplacian(grayImage, cv2.CV_8U, grayImage, size)
    normalizedInverseAlpha = (1.0 / 255) * (255 - grayImage)
    channels = cv2.split(image)
    for channel in channels:
        channel[:] = channel * normalizedInverseAlpha
    return cv2.merge(channels)

def extractMainColor(image, mask):
    """
    提取彩色图像的主颜色（针对单色图像）

    Args:
        image 图像
    Return:
        color 主颜色
    """
    color = [0,0,0]
    for channel in [0,1,2]:
        hist = cv2.calcHist(
            images=[image],
            channels= [channel],
            mask=mask,
            histSize=[32],
            ranges=[0, 255]
        )
        color[channel] = np.argmax(hist) * 8
    return color

def cut(image):
    """图像分割

    Args:
        image 原图像
    Return:
        dst 目标图像
    """
    w = image.shape[0]
    h = image.shape[1]
    mask = np.zeros((w, h), np.uint8)

    # bgdModel = np.zeros((1, 65), np.float64)
    # fgdModel = np.zeros((1, 65), np.float64)

    # 标识前景区域
    rect = (0, 0, w, h)
    # 进行grabcut，迭代次数为5次
    cv2.grabCut(image, mask, rect, None, None, 5, cv2.GC_INIT_WITH_RECT)

    # 将背景颜色设置为0
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    dst = image * mask2[:, :, np.newaxis]
    return dst

def mapColor(color):
    """
    获得颜色映射

    Args:
        color 颜色
    Return:
        dstColor 目标颜色
    """
