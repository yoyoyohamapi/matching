# coding: utf8
"""
上装特征提取
"""

import os
import cv2
import json
import numpy as np
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from skimage.feature import greycomatrix, greycoprops

with open("../config/web_safe_color.json") as clothingColorConfig:
    colorMap = json.load(clothingColorConfig)

flatten = lambda l: [item for sublist in l for item in sublist]


def createFeatureExtractor(image, mask, dp, filename, debug=False):
    """
    创建特征提取器

    Args:
        image 图像
        mask 图像掩膜
        debug 是否开启debug模式
    Returns:
        extract 提取特征
    """
    reduceRatio = 0.5
    rows, cols, _ = image.shape
    # image = cv2.resize(image, (0,0), fx=reduceRatio, fy=reduceRatio)
    # image = cv2.pyrDown(image, (rows/2, cols/2))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # mask = cv2.resize(mask, (0,0), fx=reduceRatio, fy=reduceRatio)
    # mask = cv2.pyrDown(mask, (rows/2, cols/2))
    cv2.threshold(mask, 200, 1, cv2.THRESH_BINARY, mask)

    def _debug(suffix, image):
        """
        调试函数

        Args:
            suffix 文件前缀
            image 图像
        """
        if debug is True:
            dstPath = os.path.join(dp, "%s_%s.jpg" % (filename, suffix))
            cv2.imwrite(dstPath, image)

    def _masking(src):
        """
        掩膜计算
        """
        return src * mask[:, :, np.newaxis]

    def _edgeDetection(image):
        """
        边缘检测

        Args:
            image 原图像
        Returns:
            edgesImg 边缘图像
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edgesImg = cv2.Canny(gray, 100, 150, apertureSize=3)
        _debug("edges", edgesImg)
        return edgesImg

    def _extractContours(image):
        """
        提取轮廓特征
            - 轮廓数

        只提取衣物内轮廓
        Args:
            image 原图像
        Returns:
            feature 轮廓特征
        """
        # 先做canny边缘提取
        image = cv2.GaussianBlur(image, (5, 5), 0)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 150, apertureSize=3)
        _, contours, hierachy = cv2.findContours(
            edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )
        rows, cols, _ = image.shape
        minContoursCount = 100
        contourDrawing = np.zeros((rows, cols), np.uint8)
        outer = 0
        count = 0
        countoursCount = len(contours)
        # 轮廓粘连了最外部轮廓
        if countoursCount > minContoursCount:
            count = countoursCount
            for idx, item in enumerate(hierachy[0]):
                cv2.drawContours(contourDrawing, contours,
                                 idx, (255, 255, 255), 1)
        else:
            for idx, item in enumerate(hierachy[0]):
                if item[3] == -1:
                    outer = idx
                    cv2.drawContours(contourDrawing, contours,
                                     idx, (0, 255, 0), 1)
                if item[3] != -1 and item[3] != outer and cv2.arcLength(contours[idx], True) > 50:
                    count = count + 1
                    # 只绘制内部轮廓
                    cv2.drawContours(contourDrawing, contours,
                                     idx, (255, 255, 255), 1)

        _debug("contours", contourDrawing)
        return [count]

    def _extractPatterns(image):
        """
        提取图案特征

        Args:
            image 原图像
        Return:
            feature 图案特征
        """
        # 先做canny边缘提取
        rows, cols, _ = image.shape
        contourDrawing = np.zeros((rows, cols, 3), np.uint8)
        image = cv2.GaussianBlur(image, (5, 5), 0)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 提取最外轮廓
        edges = cv2.Canny(mask * 255, 100, 150, apertureSize=3)
        _, contours, hierachy = cv2.findContours(
            edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        maxContour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour) > cv2.contourArea(maxContour):
                maxContour = contour
        maxContourArea = cv2.contourArea(maxContour)
        maxContourMask = np.zeros((rows, cols), np.uint8)
        cv2.drawContours(maxContourMask, [maxContour], 0, 1, 15)
        cv2.drawContours(contourDrawing, [maxContour], 0, (0, 255, 0), 15)
        # 提取内部轮廓（图案）
        gray[mask == 0] = 0
        edges = cv2.Canny(gray, 50, 100, apertureSize=3)
        _debug("edges_pattern", edges)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        # 淘汰外部轮廓
        edges[maxContourMask != 0] = 0
        # 淘汰领标图案
        maxContourRect = cv2.boundingRect(maxContour)
        x, y, w, h = maxContourRect
        edges[y:y + 60, x + w / 3:x + w * 2 / 3] = 0
        _debug("inner_edges", edges)
        _, contours, hierachy = cv2.findContours(
            edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
        )

        totalArea = 0
        largeAreas = 0
        if hierachy is not None:
            for idx, item in enumerate(hierachy[0]):
                contour = contours[idx]
                area = cv2.contourArea(contour)
                boundingRect = cv2.boundingRect(contour)
                x, y, w, h = boundingRect
                rectArea = w * h
                totalArea = totalArea + area
                # 统计大轮廓的数目
                if item[2] != -1 and rectArea > 2000:
                    largeAreas = largeAreas + 1
                    cv2.drawContours(contourDrawing, contours,
                                     idx, (255, 255, 255), cv2.FILLED)

        _debug("patterns", contourDrawing)

        # 检测出的轮廓面积占比,
        return [totalArea / float(maxContourArea), largeAreas]

    def _extractPatterns2(image):
        """
        图案提取 2.0

        Args:
            image 源图像
        Return:
            feature 图案特征
        """
        rows, cols, _ = image.shape
        # resized = cv2.pyrDown(image, (rows/2, cols/2))
        # rows, cols, _ = resized.shape
        contourDrawing = np.zeros((rows, cols, 3), np.uint8)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 提取最外轮廓
        edges = cv2.Canny(mask * 255, 100, 150, apertureSize=3)
        _, contours, hierachy = cv2.findContours(
            edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        maxContour = contours[0]
        for contour in contours:
            if cv2.contourArea(contour) > cv2.contourArea(maxContour):
                maxContour = contour
        maxContourBounding = cv2.boundingRect(maxContour)
        roi = np.zeros((rows, cols), np.uint8)
        x, y, w, h = maxContourBounding
        roi[y + 60:y + 5 * h / 6 - 60, x + w / 4:x + 3 * w / 4] = 255
        maxContourArea = cv2.contourArea(maxContour)
        maxContourMask = np.zeros((rows, cols), np.uint8)
        cv2.drawContours(maxContourMask, [maxContour], 0, 1, 15)
        cv2.drawContours(contourDrawing, [maxContour], 0, (0, 255, 0), 15)
        # 提取内部轮廓（图案）
        gray[mask == 0] = 0
        gray[maxContourMask == 1] = 0
        top = y + 60
        bottom = y - 60 + h - 20
        vAxis = top + (bottom - top) / 2
        left = x + w / 4
        right = x + 3 * w / 4
        hAxis = left + (right - left) / 2
        # full roi
        full = gray[top:bottom, left:right]
        # top left roi
        topLeft = gray[top:vAxis, left:hAxis]
        # bottom left roi
        bottomLeft = gray[vAxis:bottom, left:hAxis]
        # top right roi
        topRight = gray[top:vAxis, hAxis:right]
        # bottom right roi
        bottomRight = gray[vAxis:bottom, hAxis:right]
        drawing = np.zeros((rows, cols, 3), np.uint8)
        fd = cv2.xfeatures2d.SURF_create(8000)
        points = []
        for idx, roi in enumerate([full, topLeft, bottomLeft, topRight, bottomRight]):
            keypoints, descriptor = fd.detectAndCompute(roi, None)
            points.append(len(keypoints))
        # 计算各个区域关键点数目的方差, 均值
        pointsMean = np.mean(points[1:])
        totalCount = points[0]
        if totalCount == 0 :
            ratio = 0
        else:
            ratio = pointsMean/totalCount
        return [ratio, totalCount]

    def _extractStripes(image):
        """
        条纹检测

        Args:
            image 原图像
        Returns:
            feature 条纹特征
        """
        # 先从水平、垂直方向进行Sobel边缘检测
        image = cv2.GaussianBlur(image, (5, 5), 0)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 锐化
        edges = cv2.Laplacian(gray, cv2.CV_8U, ksize=3)
        _debug("edges_laplacian", edges)
        # edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        horizontalEdges = cv2.Sobel(edges, cv2.CV_8U, 0, 1, ksize=5)
        verticalEdges = cv2.Sobel(edges, cv2.CV_8U, 1, 0, ksize=5)
        _debug("edges_horizontal", horizontalEdges)
        _debug("edges_vertical", verticalEdges)
        rows, cols, _ = image.shape
        # 最少线条数
        minLines = 3
        # 两种条纹模式
        HORIZONTAL_MODE = 0
        VERTICAL_MODE = 1

        # 获得条纹检测的roi
        _, contours, hierachy = cv2.findContours(
            mask.copy(),
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        boundingRect = cv2.boundingRect(contours[0])
        x, y, w, h = boundingRect
        roiX = x + w / 4
        roiW = w - 2 * w / 4
        neckH = h / 10
        roiY = y + neckH  # 刨除领口部分
        roiH = h / 2
        fullRoi = [
            roiX,
            roiY,
            roiW,
            h
        ]
        topRoi = [
            roiX,
            roiY,
            roiW,
            roiH
        ]
        bottomRoi = [
            roiX,
            roiY + roiH,
            roiW,
            h - (neckH + roiH)
        ]
        rectDrawing = edges.copy()
        rectDrawing = cv2.cvtColor(rectDrawing, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(
            rectDrawing,
            (bottomRoi[0], bottomRoi[1]),
            (bottomRoi[0] + bottomRoi[2], bottomRoi[1] + bottomRoi[3]),
            (174, 137, 255),
            3
        )
        cv2.rectangle(
            rectDrawing,
            (topRoi[0], topRoi[1]),
            (topRoi[0] + topRoi[2], topRoi[1] + topRoi[3]),
            (62, 255, 233),
            3
        )

        """
        提取roi区域的线条特征

        Args:
            roi 感兴趣的区域
            color 绘制rect用
            name 命名
        Return:
            feature 特征
        """
        def _extract(roi, color, name):
            feature = []
            x, y, w, h = roi
            # 横条纹的最小宽度，最小比例系数
            minHorizontalLen = w * 0.8
            minHorizontalRatio = minHorizontalLen / 30.0
            # 竖条纹的最小长度
            minVerticalLen = h * 0.7
            minVerticalRatio = minVerticalLen / 30.0

            # 获得各个连通域的最小外接矩形(区分横条纹，竖条纹)
            horizontalRects = []
            verticalRects = []

            roiMask = np.zeros((rows, cols), np.uint8)
            roiMask[y:y + h, x:x + w] = 1
            _debug("roi_mask", roiMask)

            for idx, edges in enumerate([horizontalEdges, verticalEdges]):
                # 获得roi区域的二值图像
                _, binary = cv2.threshold(edges, 150, 255, cv2.THRESH_BINARY)
                _debug("edges_binary_%d" % (idx), binary)
                binary = cv2.bitwise_and(binary, binary, mask=roiMask)
                _debug("binary_%s_%d" % (name, idx), binary)

                # 获得二值图像的连通域
                _, contours, hierachy = cv2.findContours(
                    binary.copy(),
                    cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_NONE
                )

                for contour in contours:
                    rect = list(cv2.boundingRect(contour))
                    area = cv2.contourArea(contour)
                    # ratio = area/(rect[2] * rect[3])
                    ratio = float(rect[2]) / rect[3]
                    rect.append(ratio)
                    # 添加时不能有交集
                    intersected = False
                    if rect[2] > minHorizontalLen and \
                            float(rect[2]) / rect[3] > minHorizontalRatio and \
                            idx == 0:
                        # 如果宽度合法，则添加到水平矩形集中
                        for x, y, w, h, ratio in horizontalRects:
                            endY = y + h
                            if (rect[1] <= endY and rect[1] >= y) or \
                                    (y <= rect[1] + rect[3] and y >= rect[1]):
                                intersected = True
                                break
                        if intersected is False:
                            horizontalRects.append(rect)
                    if rect[3] > minVerticalLen and \
                            float(rect[3]) / rect[2] > minVerticalRatio and \
                            idx == 1:
                        # 如果高度合法，则添加到竖直矩形集中
                        for x, y, w, h, ratio in horizontalRects:
                            endX = x + w
                            if (rect[0] <= endX and rect[0] >= x) or \
                                    (x <= rect[0] + rect[2] and x >= rect[0]):
                                intersected = True
                                break
                        if intersected is False:
                            verticalRects.append(rect)

            # 只保留最多方向的条纹
            dists = []
            if len(horizontalRects) > len(verticalRects):
                rects = horizontalRects
                # 对rects进行排序
                rects = sorted(rects, key=lambda rect: rect[1])
                # 计算平均间距
                length = len(rects)
                for idx, rect in enumerate(rects):
                    if idx + 1 != length:
                        nextRect = rects[idx + 1]
                        dist = nextRect[1] - rect[1]
                        dists.append(dist)
                stripeMode = HORIZONTAL_MODE
            else:
                rects = verticalRects
                # 对rects进行排序
                rects = sorted(rects, key=lambda rect: rect[0])
                # 计算平均间距
                length = len(rects)
                for idx, rect in enumerate(rects):
                    if idx + 1 != length:
                        nextRect = rects[idx + 1]
                        dist = nextRect[0] - rect[0]
                        dists.append(dist)
                stripeMode = VERTICAL_MODE

            for x, y, w, h, ratio in rects:
                cv2.rectangle(rectDrawing, (x, y), (x + w, y + h), color, 1)

            # 对于横条纹，求取长度的方差，求取起始坐标的方差
            rects = np.array(rects)
            lines = len(rects)
            # 如果线条数过少，或者线条间距存在问题
            if lines >= minLines and np.mean(dists) <= roi[3] * 0.3:
                devX = np.std(rects[:, 0])
                devW = np.std(rects[:, 2])
                devY = np.std(rects[:, 1])
                devH = np.std(rects[:, 3])
                devRatio = np.std(rects[:, 4])
                devDist = np.std(dists)
            else:
                devX = devY = devW = devH = devRatio = devDist = -100

            _debug("rects", rectDrawing)

            if stripeMode == HORIZONTAL_MODE:
                feature = [devX, devW]
            else:
                feature = [devY, devH]
            feature = feature + [devRatio, devDist]
            return lines, feature
        rois = [
            (topRoi, (0, 255, 0), "top"),
            (bottomRoi, (255, 0, 0), "bottom"),
            (fullRoi, (0, 0, 255), "full")
        ]
        # 仅保留提取线条最多的
        maxLines = 0
        feature = []
        for roi, color, name in rois:
            lines, f = _extract(roi, color, name)
            if lines >= maxLines:
                maxLines = lines
                feature = f
        return feature

    def _extractColors(image):
        freq = {}
        for color in ['white', 'brown', 'orange', 'black', 'gray', 'yellow', 'blue', 'green', 'red', 'purple', 'pink']:
            freq[color] = 0
        hexFreq = {}
        """
        提取颜色特征
        Args:
            image 原图像
            edgesImg 边缘图像
        Returns:
            feature 颜色特征
        """
        # 转换为web safe color
        rows, cols, _ = image.shape
        resized = cv2.pyrDown(image.copy(), (rows/2, cols/2))
        resizedMask = cv2.pyrDown(mask.copy(), (rows/2, cols/2))
        webSafeImg = np.array(resized, dtype=np.uint16)
        webSafeImg = np.floor((webSafeImg + 25) / float(51)) * 51
        # 缩小
        _debug("web_safe", webSafeImg)
        rows, cols, _ = webSafeImg.shape
        colorImage = np.zeros((rows, cols, 3), np.uint8)
        for row in range(rows):
            for col in range(cols):
                if resizedMask[row, col] != 0:
                    b, g, r = webSafeImg[row, col]
                    rgbColor = sRGBColor(
                        rgb_r=r, rgb_b=b, rgb_g=g, is_upscaled=True)
                    hex = rgbColor.get_rgb_hex()
                    color = colorMap[hex]
                    if hex in hexFreq:
                        hexFreq[hex] = hexFreq[hex] + 1
                    else:
                        hexFreq[hex] = 1
                    if color in freq:
                        freq[color] = freq[color] + 1
                    else:
                        freq[color] = 1
                    colorImage[row, col] = (b, g, r)
        # 获得占比最多的颜色
        maxValue = 0
        hexFreqItems = hexFreq.items()
        maxColor, _ = hexFreqItems[0]
        for (k,v) in hexFreqItems:
            if v > maxValue:
                maxValue = v
                maxColor = k
        _debug("color_distribution", colorImage)
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
        # 占比的均值和方差（前三个）
        ratios = sorted(ratios, reverse=True)[:3]
        return [maxColor] +ratios

    def _extractGLCM(image):
        """
        提取灰度共生矩阵纹理特征

        Args:
            image 原图像
        Return:
            feature
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        g = greycomatrix(gray, [5], [0, np.pi/4, np.pi/2, 3*np.pi/4], 256, symmetric=True, normed=True)
        asm = greycoprops(g, 'ASM')
        homogeneity = greycoprops(g, 'homogeneity')
        dissimilarity = greycoprops(g, 'dissimilarity')
        print 'asm:', asm
        print 'homogeneity:', homogeneity
        print 'dissimilarity:', dissimilarity
        return np.concatenate((asm,homogeneity,dissimilarity), axis=1)[0,:]

    def extract():
        # step3：特征提取
        extractors = [_extractColors, _extractPatterns2, _extractPatterns, _extractStripes, _extractGLCM]
        features = [extractor(image) for extractor in extractors]
        print len(flatten(features))
        return flatten(features)

    _debug("src", image)

    return {
        "extract": extract
    }
