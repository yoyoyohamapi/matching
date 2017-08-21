# coding: utf8
"""
颜色工具集

"""

import cv2
import numpy as np
import time
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_diff import delta_e_cie2000, delta_e_cie1994
from colormath.color_conversions import convert_color

def isColdColor(hex):
    """
    判断某hex代码是否是冷色

    Args:
        hex
    Returns:
        是否冷色
    """
    r,g,b = hex2Rgb(hex)
    if r > b:
        return False
    else:
        return True

def _tupleDist(a, b):
    """
    计算两个tuple的欧式距离

    Args:
        a tuple1
        b tuple2
    Returns:
        dist 欧氏距离
    """
    aArr = np.array(a)
    bArr = np.array(b)
    return np.linalg.norm(aArr - bArr)


def hex2Rgb(value):
    """
    hex颜色代码转换为RGB颜色代码

    Args:
        value hex颜色代码
    Returns:
        rgb
    """
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def hex2Bgr(value):
    """
    hex颜色代码转换为BGR颜色代码

    Args:
        value hex颜色代码
    Returns:
        brgColor
    """
    rgb = hex2Rgb(value)
    bgr = (rgb[2], rgb[1], rgb[0])
    return bgr


def rgb2Hex(value):
    """
    rgb颜色代码转换为hex颜色代码

    Args:
        value rgb颜色代码
    Returns:
        hex
    """
    return ('#%02x%02x%02x' % value).upper()


def bgr2Hex(value):
    """
    bgr颜色代码转换为hex颜色代码

    Args:
        value bgr颜色
    Returns:
        hex
    """
    return ('#%02x%02x%02x' % (value[2], value[1], value[0])).upper()

def extractMainColor(image, mask, colorMap=None):
    """
    提取彩色图像的主颜色（针对单色图像）

    Args:
        image 图像
        mask 掩膜
        colorMap 预设颜色集
    Return:
        mainColor 主颜色
        hex 主颜色代码
        colorName 颜色名称
    """
    # 初始化颜色
    mainColor = [0, 0, 0]
    rows, cols, channels = image.shape
    if colorMap is None:
        # 三个通道的主颜色进行融合
        for channel in [0, 1, 2]:
            hist = cv2.calcHist(
                images=[image],
                channels=[channel],
                mask=mask,
                histSize=[32],
                ranges=[0, 255]
            )
            mainColor[channel] = np.argmax(hist) * 8
        return mainColor, bgr2Hex(mainColor)
    else:
        # 计算图像颜色与预设颜色的距离
        minDist = float("inf")
        colorName = colorMap.keys()[0]
        mainColor = colorMap[colorName][0]
        for color in colorMap.keys():
            colors = colorMap[color]
            for hex in colors:
                bgr = hex2Bgr(hex)
                colorImage = np.ones((rows, cols, 3), np.uint8) * bgr
                diff = cv2.subtract(image, colorImage,
                                    mask=mask, dtype=cv2.CV_32S)
                dist = np.mean(np.abs(diff))
                if dist < minDist:
                    minDist = dist
                    mainColor = bgr
                    colorName = color
        return mainColor, bgr2Hex(mainColor), colorName

def createColorExtracter(colorMap):
    colors = []
    def getColor(pixel):
        bgr = image[row, col]
        hex = bgr2Hex(bgr).lower()
        color = colorMap[hex]
        if color in freq:
            freq[color] = freq[color] + 1
        else:
            freq[color] = 0
    getColorFunc = np.vectorize(getColor)

    def extractColors(image, mask):
        freq = {}
        # for color in ['white', 'brown', 'orange', 'black', 'gray', 'yellow', 'blue', 'green', 'red', 'purple', 'pink']:
        #     freq[color] = 0
        for i in range(20):
            image = cv2.GaussianBlur(image, (3,3), 0)
        # 做一个亮度提升
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        channels = cv2.split(image)
        _, channels[2] = cv2.threshold(channels[2], 200, 255, cv2.THRESH_TRUNC)
        image = cv2.merge(channels)
        image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
        # 转换为web safe color
        image = np.array(image, dtype=np.uint16)
        image = np.floor((image + 25) / float(51)) * 51
        rows, cols, _ = image.shape
        colorImage = np.zeros((rows, cols, 3), np.uint8)
        for row in range(rows):
            for col in range(cols):
                if mask[row, col] != 0:
                    bgr = image[row, col]
                    hex = bgr2Hex(bgr).lower()
                    color = colorMap[hex]
                    if color in freq:
                        freq[color] = freq[color] + 1
                    else:
                        freq[color] = 1
                    colorImage[row, col] = bgr
        # if freq["gray"] > 10000:
            # freq["gray"] = freq["gray"] - 10000
        print freq
        cv2.imshow("color", colorImage)
        cv2.waitKey(0)
        # 求取各个颜色的占比，占比过小的淘汰
        values = freq.values()
        count = sum(values)
        ratios = []
        for value in values:
            ratio = float(value) / count
            # if ratio > 0.1:
            ratios.append(ratio)
        # maxValue = np.max(ratios)
        # mean = np.mean(ratios)
        # std = np.std(ratios)
        # 占比的均值和方差
        return sorted(ratios, reverse=True)[:3]
    return extractColors


def extractColorMoments(image, mask=None):
    """
    颜色矩特征提取， 用于判断衣物的聚类：
    - 纯色
    - 撞色
    - 彩色

    Args:
        image 原图像
        mask 掩膜
    Returns:
        feature
    """
    rows, cols, _ = image.shape
    channels = cv2.split(image)
    features = []

    for channel in channels:
        mean = cv2.mean(channel, mask)[0]
        diff = channel - mean
        variance = np.power(cv2.mean(diff**2, mask)[0], 0.5)
        skewnesses = np.power(cv2.mean(diff**2, mask)[0], 1.0 / 3.0)
        features = features + [mean, variance, skewnesses]
    return features


def createColorDistsExtracter(shape, colorMap):
    colorImages = {}

    def extractColorDists(image, mask):
        """
        颜色距离特征提取

        Args:
            image 图像
            mask 图像掩膜
        Return:
            features
        """
        dists = []
        rows, cols, _ = image.shape
        for color in colorImages.keys():
            minDist = float("inf")
            for colorImage in colorImages[color]:
                diff = cv2.subtract(image, colorImage,
                                    mask=mask, dtype=cv2.CV_32S)
                dist = np.mean(np.abs(diff))
                if dist < minDist:
                    minDist = dist
            dists.append(minDist)
        # 排序
        dists = np.divide(dists, float(min(dists)))
        sortedDists = sorted(dists, reverse=True)
        return sortedDists[:len(sortedDists) - 1]

    for color in colorMap.keys():
        images = []
        colors = colorMap[color]
        for hex in colors:
            bgr = hex2Bgr(hex)
            image = np.ones(shape, dtype=np.uint8) * bgr
            images.append(image)
        colorImages[color] = images

    return extractColorDists

def mapColor(colorMap, color):
    """
    获得颜色映射

    Args:
        colorMap 颜色映射表
        color 颜色
    Return:
        dstColor 匹配到的颜色值
    """
    # 计算最近颜色值
    colors = colorMap.keys()
    dstColor = None
    minDist = float("Inf")
    b, g, r = color
    labColor = convert_color(sRGBColor(r,g,b,True), LabColor)
    for key in colors:
        colorList = colorMap[key]
        for hexColor in colorList:
            r,g,b = hex2Rgb(hexColor)
            rgb = sRGBColor(r,g,b,True)
            lab = convert_color(rgb, LabColor)
            dist = delta_e_cie1994(lab, labColor)
            if dstColor is None or dist < minDist:
                minDist = dist
                colorName = key
                dstColor = hexColor
    return dstColor, colorName
